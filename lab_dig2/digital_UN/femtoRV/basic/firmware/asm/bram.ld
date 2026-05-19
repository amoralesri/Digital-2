MEMORY {
   BRAM (RWX) : ORIGIN = 0x0000, LENGTH = 0x4000  /* 6kB RAM */
}
SECTIONS
{
    everything :
    {
        . = ALIGN(4);
        call_mult.o (.text)
        *(.*)
    } >BRAM
}
