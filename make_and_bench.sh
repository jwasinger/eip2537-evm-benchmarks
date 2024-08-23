#! /usr/bin/env bash

tmp_file=$(mktemp)
python3 build_benchmark_contract.py templates/benchmark.huff.tmpl > contracts/benchmark.huff
huffc --bytecode contracts/benchmark.huff -r 2>&1 | python3 capture_huffc_output.py > $tmp_file

input=$(python3 gen_bench_input.py $PRECOMPILE $INPUT_COUNT)

~/projects/go-ethereum/build/bin/evm --codefile $tmp_file --input $input --prestate ./genesis.json --bench run 2>&1
