from PIL import Image, ImageSequence, ImageEnhance
import numpy as np
import sys
import os

if len(sys.argv) < 2:
    print("Uso: python gif_to_h.py <archivo.gif>")
    sys.exit(1)

nombre_archivo = sys.argv[1]
base_name = os.path.basename(nombre_archivo).split(".")[0]
var_name = "gif_" + base_name  # Ejemplo: gif_goku

try:
    im = Image.open(nombre_archivo)
except:
    print(f"Error: No se puede abrir {nombre_archivo}")
    sys.exit(1)

# Obtener todos los frames
frames = [frame.copy() for frame in ImageSequence.Iterator(im)]
num_frames = len(frames)
print(f"Procesando GIF '{base_name}' con {num_frames} frames...")

nombre_salida = f"{base_name}.h"

with open(nombre_salida, "w") as f:
    f.write(f"#ifndef _{base_name.upper()}_H\n")
    f.write(f"#define _{base_name.upper()}_H\n\n")
    f.write(f"#include <stdint.h>\n\n")
    
    # Definimos la cantidad de frames para usarla en el C
    f.write(f"#define {var_name.upper()}_FRAMES {num_frames}\n\n")
    
    # Creamos una Matriz 2D: [NUM_FRAMES][2048]
    f.write(f"const uint32_t {var_name}[{num_frames}][2048] = {{\n")

    for i, frame in enumerate(frames):
        # 1. Convertir a RGB
        frame = frame.convert('RGB')

        # 2. Redimensionar (LANCZOS para calidad, o NEAREST si es pixel art puro)
        # Si es Pixel Art puro, cambia LANCZOS por NEAREST abajo:
        if frame.size != (64, 64):
            frame = frame.resize((64, 64), Image.Resampling.NEAREST)

        # 3. Mejora de contraste (Opcional, pero recomendado para LEDs)
        enhancer = ImageEnhance.Contrast(frame)
        frame = enhancer.enhance(1.2)
        
        img = np.array(frame)

        f.write("    {\n") # Inicio del frame
        
        # 4. Lógica de empaquetado (La tuya con >> 5)
        for y in range(32):
            for x in range(64):
                # Mitad superior
                r1 = (img[y, x, 2] >> 5) 
                g1 = (img[y, x, 1] >> 5)
                b1 = (img[y, x, 0] >> 5)

                # Mitad inferior
                r2 = (img[y+32, x, 2] >> 5)
                g2 = (img[y+32, x, 1] >> 5)
                b2 = (img[y+32, x, 0] >> 5)

                # Empaquetado de bytes
                byte1 = (r1 << 4) | g1
                byte2 = (b1 << 4) | r2
                byte3 = (g2 << 4) | b2

                # Corrección Little Endian (La que arregló la lluvia)
                value32 = byte1 | (byte2 << 8) | (byte3 << 16)

                f.write(f"0x{value32:06X},")
        
        f.write("    },\n") # Fin del frame

    f.write("};\n\n")
    f.write(f"#endif\n")

print(f"¡Listo! Archivo generado: {nombre_salida}")
print(f"Variable a usar en C: {var_name}")