#! /usr/bin/env bash

python3 build_benchmark_contract.py templates/benchmark.huff.tmpl > contracts/benchmark.huff

bytecode=$(huffc --bytecode contracts/benchmark.huff -r 2>&1 | python3 capture_huffc_output.py)
input=$(python3 gen_bench_input.py)

~/projects/go-ethereum/build/bin/evm --code $bytecode --input $input --prestate ./genesis.json run --bench 2>&1
echo "done"
