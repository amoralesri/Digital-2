import socket
import time
import sys
import os
import numpy as np
from PIL import Image

# --- CONFIGURACIÓN ---
FPGA_IP = "10.42.0.220"
FPGA_PORT = 1234
CHUNK_SIZE = 1024 

if len(sys.argv) < 2:
    print("Uso: python enviar_panel.py <imagen.png>")
    sys.exit(1)

nombre_imagen = sys.argv[1]

# 1. PROCESAR IMAGEN
im = Image.open(nombre_imagen)
if im.mode != 'RGB':
    im = im.convert('RGB')

im = im.resize((64, 64), resample=Image.NEAREST)
img = np.array(im)

print(f"Procesando {nombre_imagen}...")

buffer_datos = bytearray()

# y = 0..31 (mitad superior), y+32 (mitad inferior)
for y in range(32):
    for x in range(64):
        # === LÓGICA REPLICADA EXACTAMENTE DE TU SCRIPT ORIGINAL ===
        
        # PIL Array -> [y, x, 0]=Rojo, [y, x, 1]=Verde, [y, x, 2]=Azul
        
        # Mitad Superior
        # Tu script original asignaba: r1 = index 2 (Azul), b1 = index 0 (Rojo)
        r1 = (img[y, x, 2] >> 5) 
        g1 = (img[y, x, 1] >> 5)
        b1 = (img[y, x, 0] >> 5)

        # Mitad Inferior (y+32)
        r2 = (img[y+32, x, 2] >> 5)
        g2 = (img[y+32, x, 1] >> 5)
        b2 = (img[y+32, x, 0] >> 5)
        
        # Empaquetado (Idéntico a tu script)
        # Byte1: R1[3:0] G1[3:0]
        byte1 = (r1 << 4) | g1
        # Byte2: B1[3:0] R2[3:0]
        byte2 = (b1 << 4) | r2
        # Byte3: G2[3:0] B2[3:0]
        byte3 = (g2 << 4) | b2

        # Agregamos los 4 bytes (00 + datos) para enviar por UDP
        buffer_datos.append(0)
        buffer_datos.append(byte1)
        buffer_datos.append(byte2)
        buffer_datos.append(byte3)

# 2. ENVIAR POR UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
total_bytes = len(buffer_datos)
print(f"Enviando {total_bytes} bytes a {FPGA_IP}...")

for i in range(0, total_bytes, CHUNK_SIZE):
    chunk = buffer_datos[i:i+CHUNK_SIZE]
    sock.sendto(chunk, (FPGA_IP, FPGA_PORT))
    time.sleep(0.002) 

print("¡Imagen enviada con corrección BGR!")