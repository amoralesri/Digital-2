from PIL import Image
import numpy as np
import sys
import os

# Uso: python png_to_npy.py ../images/flag.png
if len(sys.argv) < 2:
    print("Uso: python png_to_npy.py <ruta_imagen.png>")
    sys.exit(1)

nombre_imagen = sys.argv[1]

if not os.path.exists(nombre_imagen):
    print(f"Error: No se encontró el archivo '{nombre_imagen}'")
    sys.exit(1)

im = Image.open(nombre_imagen)

if im.mode != 'RGB':
    im = im.convert('RGB')

if im.size != (64, 64):
    print(f"Advertencia: la imagen es {im.size}, se redimensionará a 64x64.")
    im = im.resize((64, 64))

img = np.array(im)

# Aquí vamos a generar 2048 palabras de 24 bits empaquetadas igual que en image.hex
words = []

for y in range(32):
    for x in range(64):
        # Mitad superior
        r1 = (img[y, x, 2] >> 4)
        g1 = (img[y, x, 1] >> 4)
        b1 = (img[y, x, 0] >> 4)

        # Mitad inferior
        r2 = (img[y+32, x, 2] >> 4)
        g2 = (img[y+32, x, 1] >> 4)
        b2 = (img[y+32, x, 0] >> 4)

        byte1 = (r1 << 4) | g1
        byte2 = (b1 << 4) | r2
        byte3 = (g2 << 4) | b2

        # Empaquetar como en readmemh: [23:16]=byte1, [15:8]=byte2, [7:0]=byte3
        word = (byte1 << 16) | (byte2 << 8) | byte3
        words.append(word)

words = np.array(words, dtype=np.uint32)

base_name = os.path.splitext(os.path.basename(nombre_imagen))[0]
nombre_salida = os.path.join(os.path.dirname(__file__), "..", "images", base_name + ".npy")
np.save(nombre_salida, words)

print(f"Archivo .npy generado: {nombre_salida}")
