from PIL import Image
import numpy as np
import sys

# Verificar si se proporcionó el nombre del archivo
if len(sys.argv) < 2:
    print("Uso: python script.py <nombre_imagen.png>")
    sys.exit(1)

nombre_imagen = sys.argv[1]

try:
    im = Image.open(nombre_imagen)
except FileNotFoundError:
    print(f"Error: No se encontró el archivo '{nombre_imagen}'")
    sys.exit(1)

# Convertir a RGB si está en modo paleta
if im.mode == 'P':
    im = im.convert('RGB')

img = np.array(im)

# Verificar dimensiones
if img.shape[0] != 64 or img.shape[1] != 64:
    print(f"Advertencia: La imagen debe ser 64x64. Dimensiones actuales: {img.shape[1]}x{img.shape[0]}")

# Generar archivos de salida
archivo0 = "../image0.hex"
archivo1 = "../image1.hex"

# Abrir ambos archivos para escritura
with open(archivo0, "w") as f0, open(archivo1, "w") as f1:
    
    # Procesar primera mitad (filas 0-31) -> image0.hex
    for y in range(32):
        for x in range(64):
            # Pixel en posición (x, y) - primera mitad
            r1 = (img[y, x, 2] >> 4)  # Azul como rojo
            g1 = (img[y, x, 1] >> 4)  # Verde
            b1 = (img[y, x, 0] >> 4)  # Rojo como azul
            
            # Byte 1: R1[3:0]G1[3:0]
            byte1 = (r1 << 4) | g1
            
            # Byte 2: B1[3:0] en los 4 bits superiores
            byte2 = (b1 << 4)
            
            f0.write("%02X%01X\n" % (byte1, (byte2 >> 4)))
    
    # Procesar segunda mitad (filas 32-63) -> image1.hex
    for y in range(32, 64):
        for x in range(64):
            # Pixel en posición (x, y) - segunda mitad
            r2 = (img[y, x, 2] >> 4)  # Azul como rojo
            g2 = (img[y, x, 1] >> 4)  # Verde
            b2 = (img[y, x, 0] >> 4)  # Rojo como azul
            
            # Byte 1: R2[3:0]G2[3:0]
            byte1 = (r2 << 4) | g2
            
            # Byte 2: B2[3:0] en los 4 bits superiores
            byte2 = (b2 << 4)
            
            f1.write("%02X%01X\n" % (byte1, (byte2 >> 4)))

print(f"Archivos generados: {archivo0} y {archivo1}")