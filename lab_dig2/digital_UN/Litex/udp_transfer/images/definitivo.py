#!/usr/bin/env python3
import sys
import numpy as np
from PIL import Image
from litex import RemoteClient

# ============================
# CONFIGURACIÓN DE ETHERBONE
# ============================
FPGA_IP   = "192.168.1.50"
FPGA_PORT = 1234

# Ruta al csr.csv generado por LiteX
CSR_CSV = "/home/pablo-reinel/proyecto_final/digital_UN/Litex/build/colorlight_5a_75e/csr.csv"


# ============================
# 1. CONVERSIÓN DE IMAGEN
# ============================
def convert_image(path):
    """Convierte una imagen normal a formato 12bpp (3 bytes por pixel)."""

    im = Image.open(path)

    # Asegurar RGB
    if im.mode != 'RGB':
        im = im.convert('RGB')

    # Redimensionar si no es 64x64
    if im.size != (64, 64):
        print(f"[INFO] Redimensionando {im.size} → 64x64")
        im = im.resize((64, 64), Image.NEAREST)

    img = np.array(im)
    data = []

    # EXACTAMENTE como lo espera el panel LED
    for y in range(32):     # Mitad superior
        for x in range(64): # Todas las columnas
            # Pixel superior
            r1 = img[y, x, 2] >> 5
            g1 = img[y, x, 1] >> 5
            b1 = img[y, x, 0] >> 5

            # Pixel inferior
            r2 = img[y+32, x, 2] >> 5
            g2 = img[y+32, x, 1] >> 5
            b2 = img[y+32, x, 0] >> 5

            # Empaquetado idéntico a tu FPGA
            byte1 = (r1 << 4) | g1
            byte2 = (b1 << 4) | r2
            byte3 = (g2 << 4) | b2

            value = (byte1 << 16) | (byte2 << 8) | byte3
            data.append(value)

    return data


# ============================
# 2. ESCRITURA POR ETHERBONE
# ============================
def send_to_FPGA(data):
    """Envía los 2048 valores al panel LED mediante Etherbone."""

    # ⚠️ ESTA ES LA API CORRECTA PARA TU LITEX
    wb = RemoteClient(
        host=FPGA_IP,
        port=FPGA_PORT,
        csr_csv=CSR_CSV
    )

    print(f"[INFO] Conectando a FPGA {FPGA_IP}...")
    wb.open()
    print("[OK] Conexión establecida.")

    # Activar init del panel
    wb.regs.led_panel0_init.write(1)

    # Enviar los 2048 valores
    for addr, value in enumerate(data):
        wb.regs.led_panel0_mem_w_address.write(addr)
        wb.regs.led_panel0_mem_w_data.write(value)
        wb.regs.led_panel0_we_a.write(1)
        wb.regs.led_panel0_we_a.write(0)

    wb.regs.led_panel0_init.write(0)

    wb.close()
    print("[OK] Imagen enviada correctamente al panel LED.")


# ============================
# MAIN
# ============================
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python send_image.py <imagen.png>")
        sys.exit(1)

    img_path = sys.argv[1]

    print("[INFO] Convirtiendo imagen…")
    data = convert_image(img_path)

    print("[INFO] Enviando por Etherbone…")
    send_to_FPGA(data)
