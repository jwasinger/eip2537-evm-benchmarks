#! /usr/bin/env bash

if [ -z ${INPUT_COUNT+x} ];then
	INPUT_COUNT=0
fi

if [ "$INPUT_COUNT" -gt "2047" ]; then
	bench_stats=$($GETH_EVM --codefile bytecodes/bench-one.hex --inputfile benchmark_inputs/$PRECOMPILE$INPUT_COUNT.hex --prestate ./genesis.json --bench run 2>&1 | python3 calc_stats.py)
	noop_stats=$($GETH_EVM --codefile bytecodes/noop-one.hex --inputfile benchmark_inputs/$PRECOMPILE$INPUT_COUNT.hex --prestate ./genesis.json --bench run 2>&1 | python3 calc_stats.py)
elif [ "$INPUT_COUNT" -gt "32" ]; then
	bench_stats=$($GETH_EVM --codefile bytecodes/bench-slow.hex --inputfile benchmark_inputs/$PRECOMPILE$INPUT_COUNT.hex --prestate ./genesis.json --bench run 2>&1 | python3 calc_stats.py)
	noop_stats=$($GETH_EVM --codefile bytecodes/noop-slow.hex --inputfile benchmark_inputs/$PRECOMPILE$INPUT_COUNT.hex --prestate ./genesis.json --bench run 2>&1 | python3 calc_stats.py)
else
	if [ "$INPUT_COUNT" -eq "0" ]; then
		INPUT_COUNT=""
	fi
	bench_stats=$($GETH_EVM --codefile bytecodes/bench.hex --inputfile benchmark_inputs/$PRECOMPILE$INPUT_COUNT.hex --prestate ./genesis.json --bench run 2>&1 | python3 calc_stats.py)
	noop_stats=$($GETH_EVM --codefile bytecodes/noop.hex --inputfile benchmark_inputs/$PRECOMPILE$INPUT_COUNT.hex --prestate ./genesis.json --bench run 2>&1 | python3 calc_stats.py)
fi

echo "$noop_stats,$bench_stats" | python3 measure_perf.py
