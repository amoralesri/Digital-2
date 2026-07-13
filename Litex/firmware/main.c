#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <irq.h>
#include <uart.h>
#include <console.h>
#include <generated/csr.h>

#ifndef CSR_MULT0__A_ADDR
#error "CSR_MULT0__A_ADDR no existe. Regenera el SoC LiteX incluyendo el periferico mult0."
#endif

#ifndef CSR_MULT0__B_ADDR
#error "CSR_MULT0__B_ADDR no existe. Regenera el SoC LiteX incluyendo el periferico mult0."
#endif

#ifndef CSR_MULT0_INIT_ADDR
#error "CSR_MULT0_INIT_ADDR no existe. Regenera el SoC LiteX incluyendo el periferico mult0."
#endif

#ifndef CSR_MULT0_PP_ADDR
#error "CSR_MULT0_PP_ADDR no existe. Regenera el SoC LiteX incluyendo el periferico mult0."
#endif

#ifndef CSR_MULT0_DONE_ADDR
#error "CSR_MULT0_DONE_ADDR no existe. Regenera el SoC LiteX incluyendo el periferico mult0."
#endif

typedef struct {
	char op;
	uint32_t a;
	uint32_t b;
} calc_operation_t;

static uint32_t mult_hw(uint32_t a, uint32_t b)
{
	csr_write_simple(a & 0xffff, CSR_MULT0__A_ADDR);
	csr_write_simple(b & 0xffff, CSR_MULT0__B_ADDR);

	csr_write_simple(1, CSR_MULT0_INIT_ADDR);
	csr_write_simple(0, CSR_MULT0_INIT_ADDR);

	while((csr_read_simple(CSR_MULT0_DONE_ADDR) & 0x1) == 0);

	return csr_read_simple(CSR_MULT0_PP_ADDR);
}

static void print_operation_result(const calc_operation_t *operation)
{
	uint32_t result;

	printf("%lu %c %lu = ",
		(unsigned long)operation->a,
		operation->op,
		(unsigned long)operation->b);

	switch(operation->op) {
	case '+':
		result = operation->a + operation->b;
		printf("%lu\n", (unsigned long)result);
		break;
	case '-':
		printf("%ld\n", (long)operation->a - (long)operation->b);
		break;
	case '*':
		if((operation->a > 0xffff) || (operation->b > 0xffff)) {
			printf("error: operandos mayores a 16 bits para mult0\n");
			break;
		}
		result = mult_hw(operation->a, operation->b);
		printf("%lu\n", (unsigned long)result);
		break;
	case '/':
		if(operation->b == 0) {
			printf("error: division por cero\n");
			break;
		}
		result = operation->a / operation->b;
		printf("%lu\n", (unsigned long)result);
		break;
	default:
		printf("error: operacion no soportada\n");
		break;
	}
}

int main(void)
{
	unsigned int i;
	static const calc_operation_t operations[] = {
		{'+',  5,   3},
		{'-', 10,   4},
		{'*',  7,   6},
		{'/', 20,   5},
		{'*', 255, 128},
		{'/', 15,   0},
	};

	uart_init();
	printf("Running LiteX calculator from SDRAM\n");

	for(i = 0; i < (sizeof(operations)/sizeof(operations[0])); i++) {
		print_operation_result(&operations[i]);
	}

	while(1) {
	}
	return 0;
}
