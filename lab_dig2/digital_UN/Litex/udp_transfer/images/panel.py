#!/usr/bin/env python3
import sys
import os
import socket
import struct
import time

from PIL import Image
import numpy as np

# ============================
#  CONFIGURACIÓN
# ============================
FPGA_IP   = "192.168.1.50"
FPGA_PORT = 1234  # mismo que usas con netcat

# ============================
#  CONVERSIÓN DE IMAGEN
# ============================

def convert_image_to_24b_words(path):
    """
    Convierte una imagen a los 2048 valores de 24 bits (en realidad usamos 32)
    en el mismo formato que tu script .h:
      - Imagen 64x64
      - Recorrido: y=0..31 (superior) y y+32 (inferior)
      - 4 bits por canal (>>5)
      - byte1 = R1[3:0]G1[3:0]
        byte2 = B1[3:0]R2[3:0]
        byte3 = G2[3:0]B2[3:0]
      - value = 0x00BBGGRR (24 bits metidos en un uint32)
    """
    if not os.path.exists(path):
        print(f"[ERROR] No se encontró el archivo '{path}'")
        sys.exit(1)

    im = Image.open(path)

    # Asegurar RGB
    if im.mode != "RGB":
        im = im.convert("RGB")

    # Redimensionar a 64x64 si no lo es
    if im.size != (64, 64):
        print(f"[INFO] Imagen {im.size}, redimensionando a 64x64...")
        im = im.resize((64, 64), resample=Image.NEAREST).convert("RGB")

    img = np.array(im)

    data = []  # aquí guardamos los 2048 uint32

    for y in range(32):
        for x in range(64):
            # Mitad superior
            r1 = (img[y,     x, 2] >> 5)  # canal AZUL como R1
            g1 = (img[y,     x, 1] >> 5)  # G
            b1 = (img[y,     x, 0] >> 5)  # canal ROJO como B1

            # Mitad inferior
            r2 = (img[y + 32, x, 2] >> 5)
            g2 = (img[y + 32, x, 1] >> 5)
            b2 = (img[y + 32, x, 0] >> 5)

            # Empaquetado exacto:
            # Byte1: R1[3:0] G1[3:0]
            byte1 = (r1 << 4) | g1
            # Byte2: B1[3:0] R2[3:0]
            byte2 = (b1 << 4) | r2
            # Byte3: G2[3:0] B2[3:0]
            byte3 = (g2 << 4) | b2

            value = (byte1 << 16) | (byte2 << 8) | byte3
            data.append(value)

    if len(data) != 2048:
        print(f"[WARN] data tiene {len(data)} palabras, deberían ser 2048")

    return data

# ============================
#  ENVÍO DE COMANDO SIMPLE
# ============================

def send_command(cmd_char):
    """
    Envía un solo byte por UDP:
      '1', '2', '3', '0', etc.
    Tu firmware lo interpreta para mostrar/limpiar imágenes precargadas.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    payload = cmd_char.encode("ascii")
    sock.sendto(payload, (FPGA_IP, FPGA_PORT))
    sock.close()
    print(f"[OK] Enviado comando '{cmd_char}' a {FPGA_IP}:{FPGA_PORT}")

# ============================
#  ENVÍO DE IMAGEN (PROTO IMG)
# ============================

def send_image(path):
    """
    Protocolo:
      1) Enviar paquete 'IMG'
      2) Enviar 2048 paquetes de 4 bytes (big-endian), cada uno con un uint32
         donde los 24 bits bajos son el valor empacado de la imagen.
    El firmware:
      - Recibe 'IMG' (3 bytes) → resetea índice.
      - Acumula 2048 palabras → cuando termina, las escribe en el panel.
    """
    data = convert_image_to_24b_words(path)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print(f"[INFO] Enviando cabecera 'IMG' a {FPGA_IP}:{FPGA_PORT}...")
    sock.sendto(b"IMG", (FPGA_IP, FPGA_PORT))
    time.sleep(0.01)  # pequeña pausa (opcional)

    print(f"[INFO] Enviando {len(data)} palabras (deberían ser 2048)...")

    for i, value in enumerate(data):
        # value: uint32, usamos solo 24 bits bajos, pero enviamos 4 bytes
        # en big-endian: 0x00BBGGRR → b'\x00\xBB\xGG\xRR'
        pkt = struct.pack(">I", value & 0x00FFFFFF)
        sock.sendto(pkt, (FPGA_IP, FPGA_PORT))

        # Pequeño delay para no saturar el MAC (ajusta si hace falta)
        # Puedes bajar este valor si todo va bien.
        time.sleep(0.0005)

        if (i + 1) % 256 == 0:
            print(f"  Enviadas {i + 1}/2048 palabras...")

    sock.close()
    print("[OK] Imagen enviada.")

# ============================
#  MAIN
# ============================

def usage():
    print("Uso:")
    print("  python panel_client.py cmd <caracter>")
    print("      -> Envía un comando simple ('1','2','3','0',...)")
    print("  python panel_client.py img <ruta_imagen>")
    print("      -> Convierte y envía una imagen 64x64 al panel")
    sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        usage()

    mode = sys.argv[1]

    if mode == "cmd":
        cmd = sys.argv[2]
        if len(cmd) != 1:
            print("[ERROR] El comando debe ser un solo carácter, ej: '1' ")
            sys.exit(1)
        send_command(cmd)

    elif mode == "img":
        img_path = sys.argv[2]
        send_image(img_path)

    else:
        usage()
