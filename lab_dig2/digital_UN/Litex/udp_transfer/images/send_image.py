from litex import RemoteClient
import numpy as np
import sys
import os

FPGA_IP = "192.168.1.50"   # ajusta a la IP de tu Colorlight
PORT    = 1234

if len(sys.argv) < 2:
    print("Uso: python send_image.py ../images/flag.npy")
    sys.exit(1)

ruta_npy = sys.argv[1]

if not os.path.exists(ruta_npy):
    print("No se encontró el archivo:", ruta_npy)
    sys.exit(1)

frame = np.load(ruta_npy)
if frame.shape[0] != 2048:
    print("El .npy debe tener 2048 palabras, tiene:", frame.shape[0])
    sys.exit(1)

wb = RemoteClient(host=FPGA_IP, port=PORT)
wb.open()

print("Enviando imagen a la FPGA...")

for i, word in enumerate(frame):
    wb.regs.led_panel0_mem_w_address.write(i)
    wb.regs.led_panel0_mem_w_data.write(int(word))
    wb.regs.led_panel0_we_a.write(1)
    wb.regs.led_panel0_we_a.write(0)

print("Listo.")
wb.close()
