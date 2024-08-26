#! /usr/bin/env bash

bench_stats=$($GETH_EVM --codefile bytecodes/bench.hex --input $(cat benchmark_inputs/$PRECOMPILE$INPUT_COUNT.hex) --prestate ./genesis.json --bench run 2>&1 | python3 calc_stats.py)
noop_stats=$($GETH_EVM --codefile bytecodes/noop.hex --input $input --prestate ./genesis.json --bench run 2>&1 | python3 calc_stats.py)

echo "$noop_stats,$bench_stats" | python3 measure_perf.py
