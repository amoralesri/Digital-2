#./run.sh soc_femto.v
rm -f a.out
rm -rf bench.vcd
iverilog -DBENCH -DSIM -DPASSTHROUGH_PLL -DBOARD_FREQ=10 -DCPU_FREQ=10 bench_iverilog.v $1 $2
vvp a.out
gtkwave bench.vcd

