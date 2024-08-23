#! /usr/bin/env bash

python3 build_benchmark_contract.py templates/benchmark.huff.tmpl > contracts/benchmark.huff
bytecode=$(huffc --bytecode contracts/benchmark.huff -r 2>&1 | python3 capture_huffc_output.py)

input=$(python3 gen_bench_input.py $PRECOMPILE $INPUT_COUNT)

~/projects/go-ethereum/build/bin/evm --gas 10000000000 --code $bytecode --input $input --prestate ./genesis.json --bench run 2>&1
