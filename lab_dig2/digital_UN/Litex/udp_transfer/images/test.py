from litex import RemoteClient

IP = "192.168.1.50"
PORT = 1234
CSR = "/home/pablo-reinel/proyecto_final/digital_UN/Litex/build/colorlight_5a_75e/csr.csv"

print("[INFO] Intentando conectar a Etherbone…")

try:
    wb = RemoteClient(host=IP, port=PORT, csr_csv=CSR)
    wb.open()
    print("[OK] Conexión establecida con la FPGA.")

    try:
        val = wb.regs.led_panel0_init.read()
        print("[OK] Registro leído correctamente:", val)

    except Exception as e:
        print("[ERROR] No pude leer CSR:", e)

    wb.close()

except Exception as e:
    print("[FAIL] No pude conectar con Etherbone:", e)
