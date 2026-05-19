from PIL import Image
import numpy as np
import sys

# Verificar si se proporcionó el nombre del archivo
if len(sys.argv) < 2:
    print("Uso: python script_c32.py <imagen.png>")
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

# Nombre de archivo .c
nombre_salida_c = "image_data32.c"

with open(nombre_salida_c, "w") as f:
    f.write("/* Imagen generada automáticamente (32 bits por entrada) */\n")
    f.write("#include <stdint.h>\n\n")
    f.write("const uint32_t image_data32[] = {\n")

    for y in range(32):  # Filas superiores
        for x in range(64):
            r1 = (img[y, x, 2] >> 4)
            g1 = (img[y, x, 1] >> 4)
            b1 = (img[y, x, 0] >> 4)

            r2 = (img[y+32, x, 2] >> 4)
            g2 = (img[y+32, x, 1] >> 4)
            b2 = (img[y+32, x, 0] >> 4)

            byte1 = (r1 << 4) | g1
            byte2 = (b1 << 4) | r2
            byte3 = (g2 << 4) | b2

            # Empaquetado en 32 bits: 0x00 BYTE1 BYTE2 BYTE3
            value32 = (byte1 << 16) | (byte2 << 8) | byte3

            f.write(f"    0x{value32:06X},\n")

    f.write("};\n")

print(f"Archivo generado: {nombre_salida_c}")
