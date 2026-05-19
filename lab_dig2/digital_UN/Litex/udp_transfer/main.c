#include <irq.h>
#include <stdio.h>
#include <stdlib.h>    // ← AGREGA ESTO
#include <string.h>    // ← AGREGA ESTO
#include <uart.h>
#include <console.h>   // ← ESTA ES LA CLAVE


#include <generated/csr.h>
#include <generated/mem.h>
#include <generated/soc.h>
#include <libliteeth/udp.h>

/* --- CONFIGURACIÓN --- */
#define PORT_RX 1234 
static unsigned int remote_ip[4]  = {10, 42, 0, 100}; 
static unsigned int my_ip_addr[4] = {10, 42, 0, 220};
static unsigned char my_mac_addr[6] = {0x10, 0xe2, 0xd5, 0x00, 0x00, 0x00};

/* --- MEMORIA PARA LA IMAGEN (2048 pixeles dobles) --- */
uint32_t imagen_ram[2048];
unsigned int buffer_pos = 0; // Para saber dónde vamos escribiendo

void my_uart_write(char c) {
    while (uart_txfull_read()); 
    uart_rxtx_write(c);
}
void my_puts(const char *s) {
    while(*s) { if(*s=='\n') my_uart_write('\r'); my_uart_write(*s++); }
}

/* --- TU DRIVER DE PANEL LED (Adaptado para leer de imagen_ram) --- */
void actualizar_panel(void){
    int tmp = 0;
    
 /*
    // Iniciar escritura
    led_panel0_init_write(1);
    
    for (tmp=0; tmp < 2048; tmp++){
        led_panel0_mem_w_address_write(tmp);
        led_panel0_we_a_write(1);
        
        // Escribimos el dato que tenemos en nuestra RAM
        led_panel0_mem_w_data_write(imagen_ram[tmp]);
        
        led_panel0_we_a_write(0);
        
        // Espera mínima (reducida a 1ms para que no parpadee tanto al recibir)
        // Si el panel falla, sube este valor.
        // my_busy_wait(1); 
    }
    
    // Finalizar escritura
    led_panel0_init_write(0);
*/
}

/* --- CALLBACK UDP (RECIBIR IMAGEN) --- */
void rx_callback(unsigned long src_ip, unsigned short src_port, unsigned short dst_port, void *data, unsigned long length)
{
    if(dst_port == PORT_RX) {
        uint8_t *payload = (uint8_t*)data;
        
        // Procesamos los datos de 4 en 4 bytes (00, B1, B2, B3)
        // Esto coincide con el script de Python que manda 4 bytes por pixel-doble
        for(unsigned int i=0; i<length; i+=4) {
            if(buffer_pos >= 2048) buffer_pos = 0; // Reset si llenamos
            
            // Reconstruimos el uint32_t
            // Python manda: 00, Byte1, Byte2, Byte3
            uint32_t val = (payload[i+1] << 16) | (payload[i+2] << 8) | payload[i+3];

            printf("%x \t", (unsigned int)val);
             printf("a");
            
            imagen_ram[buffer_pos] = val;
            buffer_pos++;
        }
        my_uart_write('.'); // Indicador visual de tráfico
    }
}

/* --- MAIN --- */
int main(void)
{
#ifdef CONFIG_CPU_HAS_INTERRUPT
	irq_setmask(0);
	irq_setie(1);
#endif
#ifdef CSR_UART_BASE
	uart_init();
#endif

    printf("\n=== FPGA LED PANEL UDP ===\n");

    // Limpiar imagen inicial (Negro)
    for(int i=0; i<2048; i++) imagen_ram[i] = 0;
    actualizar_panel();

    uint32_t local_ip_int  = IPTOINT(my_ip_addr[0], my_ip_addr[1], my_ip_addr[2], my_ip_addr[3]);
    
    my_puts("Iniciando UDP...\n");
    udp_start(my_mac_addr, local_ip_int);
    udp_set_callback(rx_callback);
    
    my_puts("LISTO. Envia la imagen desde Python!\n");

    while (1) {
        //Revisar red (recibir paquetes y llenar imagen_ram)
        udp_service();
        actualizar_panel();
    }
    return 0;
}
