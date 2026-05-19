/* start.S - Con configuración de STACK (Pila) */
.section .text.startup
.global _start
.global main

_start:
    /* 1. CONFIGURAR LA PILA (STACK POINTER) - CRÍTICO */
    /* Netboot carga el programa en 0x40000000. */
    /* Ponemos la pila 32KB (0x8000) más adelante para tener espacio de sobra. */
    li sp, 0x40008000
    
    /* 2. Desactivar interrupciones por seguridad */
    csrw mie, zero
    
    /* 3. Saltar a C */
    call main

loop:
    j loop
