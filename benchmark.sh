#! /usr/bin/env bash

if [ -z ${INPUT_COUNT+x} ];then
	INPUT_COUNT=1
fi

if [ "$INPUT_COUNT" -gt "32" ]; then
	bench_stats=$($GETH_EVM --codefile bytecodes/bench-slow.hex --inputfile benchmark_inputs/$PRECOMPILE$INPUT_COUNT.hex --prestate ./genesis.json --bench run 2>&1 | python3 calc_stats.py)
	noop_stats=$($GETH_EVM --codefile bytecodes/noop-slow.hex --inputfile benchmark_inputs/$PRECOMPILE$INPUT_COUNT.hex --prestate ./genesis.json --bench run 2>&1 | python3 calc_stats.py)
else
	bench_stats=$($GETH_EVM --codefile bytecodes/bench.hex --inputfile benchmark_inputs/$PRECOMPILE$INPUT_COUNT.hex --prestate ./genesis.json --bench run 2>&1 | python3 calc_stats.py)
	noop_stats=$($GETH_EVM --codefile bytecodes/noop.hex --inputfile benchmark_inputs/$PRECOMPILE$INPUT_COUNT.hex --prestate ./genesis.json --bench run 2>&1 | python3 calc_stats.py)
fi

echo "$PRECOMPILE,$INPUT_COUNT"
echo "$noop_stats,$bench_stats" | python3 measure_perf.py
