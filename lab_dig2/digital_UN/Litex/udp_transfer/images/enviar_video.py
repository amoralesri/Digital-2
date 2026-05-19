import socket
import time
import sys
import numpy as np
from PIL import Image, ImageSequence

# --- CONFIGURACIÓN ---
FPGA_IP = "192.168.1.50"
FPGA_PORT = 1234
CHUNK_SIZE = 1024 

# Velocidad de animación (Menor número = Más rápido)
# 0.05 es aprox 20 FPS. Ajusta si va muy lento o rápido.
TIEMPO_ENTRE_FRAMES = 0.05 

if len(sys.argv) < 2:
    print("Uso: python enviar_gif.py <archivo.gif>")
    sys.exit(1)

nombre_gif = sys.argv[1]
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print(f"Cargando GIF: {nombre_gif}")
try:
    gif = Image.open(nombre_gif)
except IOError:
    print("Error: No se pudo abrir el archivo GIF.")
    sys.exit(1)

print(f"Transmitiendo a {FPGA_IP}... (Presiona Ctrl+C para salir)")

try:
    while True: # Bucle infinito para que el GIF se repita
        # Iterar sobre cada cuadro del GIF
        for frame in ImageSequence.Iterator(gif):
            
            # 1. Convertir y Redimensionar
            # Convertimos a RGB porque los GIFs suelen venir en modo 'P' (Paleta)
            frame = frame.convert('RGB')
            frame = frame.resize((64, 64), resample=Image.NEAREST)
            img = np.array(frame)

            buffer_datos = bytearray()

            # 2. PROCESAMIENTO (Tu lógica BGR exacta)
            for y in range(32):
                for x in range(64):
                    # Mitad Superior
                    # img[y,x,2] es AZUL en PIL, pero lo asignamos a R1 (Swap)
                    r1 = (img[y, x, 2] >> 5) 
                    g1 = (img[y, x, 1] >> 5)
                    b1 = (img[y, x, 0] >> 5)

                    # Mitad Inferior (y+32)
                    r2 = (img[y+32, x, 2] >> 5)
                    g2 = (img[y+32, x, 1] >> 5)
                    b2 = (img[y+32, x, 0] >> 5)
                    
                    # Empaquetado
                    byte1 = (r1 << 4) | g1
                    byte2 = (b1 << 4) | r2
                    byte3 = (g2 << 4) | b2

                    buffer_datos.append(0)
                    buffer_datos.append(byte1)
                    buffer_datos.append(byte2)
                    buffer_datos.append(byte3)

            # 3. ENVIAR FRAME POR UDP
            for i in range(0, len(buffer_datos), CHUNK_SIZE):
                chunk = buffer_datos[i:i+CHUNK_SIZE]
                sock.sendto(chunk, (FPGA_IP, FPGA_PORT))
                # Pausa microscópica entre paquetes UDP para estabilidad
                time.sleep(0.001) 
            
            # 4. Esperar antes del siguiente frame
            time.sleep(TIEMPO_ENTRE_FRAMES)

except KeyboardInterrupt:
    print("\nDetenido.")
    sock.close()