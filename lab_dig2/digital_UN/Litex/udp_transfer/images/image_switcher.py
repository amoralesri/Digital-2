from litex import RemoteClient
import numpy as np
import os

FPGA_IP = "192.168.1.50"
PORT    = 1234

IMAGE_PATH = os.path.join(os.path.dirname(__file__), "..", "images")

# Lista de nombres base (sin ruta)
IMAGES = [
    "flag.npy",
    "logo.npy",
    "goku.npy",
]

def send_frame(wb, frame):
    for i, word in enumerate(frame):
        wb.regs.led_panel0_mem_w_address.write(i)
        wb.regs.led_panel0_mem_w_data.write(int(word))
        wb.regs.led_panel0_we_a.write(1)
        wb.regs.led_panel0_we_a.write(0)

def main():
    wb = RemoteClient(host=FPGA_IP, port=PORT)
    wb.open()

    while True:
        print("\n=== PANEL 64x64 - Selector de imágenes ===")
        for i, name in enumerate(IMAGES):
            print(f"{i}: {name}")
        print("x: salir")

        sel = input("Seleccione opción: ")

        if sel.lower() == "x":
            break

        try:
            idx = int(sel)
            if idx < 0 or idx >= len(IMAGES):
                print("Índice fuera de rango.")
                continue

            ruta = os.path.join(IMAGE_PATH, IMAGES[idx])
            if not os.path.exists(ruta):
                print("No existe el archivo:", ruta)
                continue

            frame = np.load(ruta)
            if frame.shape[0] != 2048:
                print("El .npy debe tener 2048 palabras.")
                continue

            print("Cargando", IMAGES[idx])
            send_frame(wb, frame)
            print("Imagen mostrada.")

        except ValueError:
            print("Entrada inválida.")

    wb.close()

if __name__ == "__main__":
    main()
