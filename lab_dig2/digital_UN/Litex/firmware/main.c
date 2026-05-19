#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <irq.h>
#include <uart.h>
#include <console.h>
#include <generated/csr.h>
void my_busy_wait(unsigned int ms)
{
	timer0_en_write(0);
	timer0_reload_write(0);
	timer0_load_write(CONFIG_CLOCK_FREQUENCY/1000*ms);
	timer0_en_write(1);
	timer0_update_value_write(1);
	while(timer0_value_read()) timer0_update_value_write(1);
}
int main(void)
{
	int tmp;
	uart_init();
	printf("Running Hola Mundo from SDRAM \n");
/*
	led_panel0_init_write(1);
    for (tmp=0; tmp <1024; tmp ++){
		led_panel0_mem_w_address_write(tmp);
		led_panel0_mem_w_data_write(tmp & 0);
	    led_panel0_we_a_write(1);
	    led_panel0_we_a_write(0);
		my_busy_wait(10);

	}
*/

	while(1) {
//		led_panel0_init_write(0);
//		my_busy_wait(1000);
//		led_panel0_init_write(1);
//		my_busy_wait(1000);
	}
	return 0;
}


