#! /usr/bin/env bash

# convert templates to huff contracts
python3 build_contract_from_template.py templates/benchmark.huff.tmpl bench > contracts/benchmark.huff
python3 build_contract_from_template.py templates/benchmark.huff.tmpl noop > contracts/noop.huff

# compile contracts to bytecodes
huffc --bytecode contracts/benchmark.huff -r 2>&1 | python3 capture_huffc_output.py > bytecodes/bench.hex
huffc --bytecode contracts/noop.huff -r 2>&1 | python3 capture_huffc_output.py > bytecodes/noop.hex

# generate the inputs
python3 gen_bench_input.py g1add > benchmark_inputs/g1add.hex
python3 gen_bench_input.py g1mul > benchmark_inputs/g1mul.hex

for input_count in {1..32}
do
python3 gen_bench_input.py g1msm $input_count > benchmark_inputs/g1msm$input_count.hex
done

python3 gen_bench_input.py g2add > benchmark_inputs/g2add.hex
python3 gen_bench_input.py g2mul > benchmark_inputs/g2mul.hex

for input_count in {1..32}
do
python3 gen_bench_input.py g2msm $input_count > benchmark_inputs/g2msm$input_count.hex
done

python3 gen_bench_input.py mapfp > benchmark_inputs/mapfp.hex
python3 gen_bench_input.py mapfp2 > benchmark_inputs/mapfp2.hex

for input_count in {1..8}
do
python3 gen_bench_input.py pairing $input_count > benchmark_inputs/pairing$input_count.hex
done
