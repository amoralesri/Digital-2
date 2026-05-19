from PIL import Image, ImageEnhance
import numpy as np
import sys

# Validación básica
if len(sys.argv) < 2:
    print("Uso: python generar_profe_fix.py <imagen.png> [nombre_variable]")
    sys.exit(1)

nombre_imagen = sys.argv[1]
nombre_variable = sys.argv[2] if len(sys.argv) > 2 else "image_data"

try:
    im = Image.open(nombre_imagen)
except FileNotFoundError:
    print(f"Error: No se encontró '{nombre_imagen}'")
    sys.exit(1)

# 1. Convertir y Redimensionar a 64x64
im = im.convert('RGB')
if im.size != (64, 64):
    print(f"Redimensionando de {im.size} a (64, 64)...")
    im = im.resize((64, 64), Image.Resampling.LANCZOS)

# 2. Mejorar imagen (Contraste y Color) para LEDs
enhancer = ImageEnhance.Contrast(im)
im = enhancer.enhance(1.5)
enhancer = ImageEnhance.Color(im)
im = enhancer.enhance(1.2)

img = np.array(im)

print(f"/* Generado con lógica del profesor para 64x64 */")
print(f"const uint32_t {nombre_variable}[] = {{")

# 3. Lógica EXACTA del profesor adaptada a C
for y in range(32):      # 32 Filas (Barrido 1/32)
    for x in range(64):  # 64 Columnas
        
        # --- PIXEL SUPERIOR (Fila y) ---
        # El profe usa BGR: [2]=Rojo(en led), [1]=Verde, [0]=Azul(en led)
        # NOTA: PIL lee RGB (0=R, 1=G, 2=B).
        # El script del profe asigna img[2] -> r1. 
        # Si tu panel es BGR, esto intercambia los canales correctamente.
        r1 = (img[y, x, 2] >> 4) & 0xF  
        g1 = (img[y, x, 1] >> 4) & 0xF
        b1 = (img[y, x, 0] >> 4) & 0xF

        # --- PIXEL INFERIOR (Fila y + 32) ---
        r2 = (img[y+32, x, 2] >> 4) & 0xF
        g2 = (img[y+32, x, 1] >> 4) & 0xF
        b2 = (img[y+32, x, 0] >> 4) & 0xF

        # --- EMPAQUETADO DEL PROFE ---
        # Byte 1: R1 G1
        byte1 = (r1 << 4) | g1
        # Byte 2: B1 R2  <-- Aquí se mezclan los pixeles de arriba y abajo
        byte2 = (b1 << 4) | r2
        # Byte 3: G2 B2
        byte3 = (g2 << 4) | b2

        # --- ARREGLO DE LA DIAGONAL (ENDIANNESS) ---
        # El procesador lee los bytes al revés (Little Endian).
        # Para que se vea bien, invertimos el orden de los bytes en el uint32.
        # Orden esperado: 0x00 [Byte3] [Byte2] [Byte1]
        value32 = byte1 | (byte2 << 8) | (byte3 << 16)

        print(f"    0x{value32:06X},")

print("};")