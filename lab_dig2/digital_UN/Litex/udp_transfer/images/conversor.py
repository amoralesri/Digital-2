from PIL import Image
import numpy as np
import sys
import os

# Uso: python png_to_hex.py ../images/imagen.png
if len(sys.argv) < 2:
    print("Uso: python png_to_hex.py <ruta_imagen.png>")
    sys.exit(1)

nombre_imagen = sys.argv[1]
nombre_imagen2= nombre_imagen.split(".",1)[0]
if not os.path.exists(nombre_imagen):
    print(f"Error: No se encontró el archivo '{nombre_imagen}'")
    sys.exit(1)

im = Image.open(nombre_imagen)

# Asegurarse de que es RGB
if im.mode != 'RGB':
    im = im.convert('RGB')

# Redimensionar a 64x64 si no lo es
if im.size != (64, 64):
    print(f"Advertencia: la imagen es {im.size}, se redimensionará a 64x64.")
    #im = im.resize((64, 64),resample=Image.NEAREST)
    im = im.resize((64, 64),resample=Image.NEAREST).convert('RGB')
    #im = im.resize((64, 64),resample=Image.NEAREST)

img = np.array(im)

# Salida (ajusta ruta si tu memory.v espera otra)
nombre_salida = os.path.join(os.path.dirname(__file__), "..", f"{nombre_imagen2}.h")

with open(nombre_salida, "w") as f:
    f.write(f"#ifndef {nombre_imagen2}\n")
    f.write(f"#define {nombre_imagen2}\n")
    f.write(f"const uint32_t {nombre_imagen2} [] =" +"{")
    # y = 0..31 (mitad superior), y+32 (mitad inferior)
    for y in range(32):
        for x in range(64):
            # Mitad superior
            # OJO: replico EXACTAMENTE el formato del profe:
            # r1 = canal AZUL, b1 = canal ROJO, todos >>4 (4 bits)
            # png_to_hex.py (alrededor de la línea 44)
            # Mitad superior
            r1 = (img[y, x, 2] >> 5) 
            g1 = (img[y, x, 1] >> 5)
            b1 = (img[y, x, 0] >> 5)

            # Repetir para la mitad inferior (y+32)
            r2 = (img[y+32, x, 2] >> 5)
            g2 = (img[y+32, x, 1] >> 5)
            b2 = (img[y+32, x, 0] >> 5)
            
            # Byte1: R1[3:0] G1[3:0]
            byte1 = (r1 << 4) | g1
            # Byte2: B1[3:0] R2[3:0]
            byte2 = (b1 << 4) | r2
            # Byte3: G2[3:0] B2[3:0]
            byte3 = (g2 << 4) | b2

            f.write("0x%02X%02X%02X,\n" % (byte1, byte2, byte3))
    
    f.write("};\n #endif")

print(f"Archivo generado: {nombre_salida}")
