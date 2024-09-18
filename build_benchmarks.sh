#! /usr/bin/env bash

# convert templates to huff contracts
python3 build_contract_from_template.py templates/benchmark.huff.tmpl bench 2850 > contracts/benchmark.huff
python3 build_contract_from_template.py templates/benchmark.huff.tmpl noop 2850 > contracts/noop.huff

python3 build_contract_from_template.py templates/benchmark.huff.tmpl bench 100 > contracts/benchmark-slow.huff
python3 build_contract_from_template.py templates/benchmark.huff.tmpl noop 100 > contracts/noop-slow.huff

python3 build_contract_from_template.py templates/benchmark.huff.tmpl bench 1 > contracts/benchmark-one.huff
python3 build_contract_from_template.py templates/benchmark.huff.tmpl noop 1 > contracts/noop-one.huff

# compile contracts to bytecodes
huffc --bytecode contracts/benchmark.huff -r 2>&1 | python3 capture_huffc_output.py > bytecodes/bench.hex
huffc --bytecode contracts/noop.huff -r 2>&1 | python3 capture_huffc_output.py > bytecodes/noop.hex

huffc --bytecode contracts/benchmark-slow.huff -r 2>&1 | python3 capture_huffc_output.py > bytecodes/bench-slow.hex
huffc --bytecode contracts/noop-slow.huff -r 2>&1 | python3 capture_huffc_output.py > bytecodes/noop-slow.hex

huffc --bytecode contracts/benchmark-one.huff -r 2>&1 | python3 capture_huffc_output.py > bytecodes/bench-one.hex
huffc --bytecode contracts/noop-one.huff -r 2>&1 | python3 capture_huffc_output.py > bytecodes/noop-one.hex

# generate the inputs
python3 gen_bench_input.py g1add > benchmark_inputs/g1add.hex
python3 gen_bench_input.py g1mul > benchmark_inputs/g1mul.hex

for input_count in {1..32}
do
python3 gen_bench_input.py g1msm $input_count > benchmark_inputs/g1msm$input_count.hex
done

python3 gen_bench_input.py g1msm 64 > benchmark_inputs/g1msm64.hex
python3 gen_bench_input.py g1msm 128 > benchmark_inputs/g1msm128.hex
python3 gen_bench_input.py g1msm 256 > benchmark_inputs/g1msm256.hex
python3 gen_bench_input.py g1msm 512 > benchmark_inputs/g1msm512.hex
python3 gen_bench_input.py g1msm 2048 > benchmark_inputs/g1msm2048.hex
python3 gen_bench_input.py g1msm 4787 > benchmark_inputs/g1msm4787.hex

python3 gen_bench_input.py g2add > benchmark_inputs/g2add.hex
python3 gen_bench_input.py g2mul > benchmark_inputs/g2mul.hex

for input_count in {1..32}
do
python3 gen_bench_input.py g2msm $input_count > benchmark_inputs/g2msm$input_count.hex
done

python3 gen_bench_input.py g2msm 64 > benchmark_inputs/g2msm64.hex
python3 gen_bench_input.py g2msm 128 > benchmark_inputs/g2msm128.hex
python3 gen_bench_input.py g2msm 256 > benchmark_inputs/g2msm256.hex
python3 gen_bench_input.py g2msm 512 > benchmark_inputs/g2msm512.hex
python3 gen_bench_input.py g2msm 2048 > benchmark_inputs/g2msm2048.hex

python3 gen_bench_input.py mapfp > benchmark_inputs/mapfp.hex
python3 gen_bench_input.py mapfp2 > benchmark_inputs/mapfp2.hex

for input_count in {1..8}
do
python3 gen_bench_input.py pairing $input_count > benchmark_inputs/pairing$input_count.hex
done
