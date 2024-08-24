#! /usr/bin/env bash

rm -f benchmark_output/evm.csv

echo "benchmark g1 add"
output=$(PRECOMPILE=g1add ./make_and_bench.sh)
echo "g1add,$output" >> benchmark_output/evm.csv

echo "benchmark g1 mul"
output=$(PRECOMPILE=g1mul ./make_and_bench.sh)
echo "g1mul,$output" >> benchmark_output/evm.csv

echo "benchmark g2 add"
output=$(PRECOMPILE=g2add ./make_and_bench.sh)
echo "g2add,$output" >> benchmark_output/evm.csv

echo "benchmark g2 mul"
output=$(PRECOMPILE=g2mul ./make_and_bench.sh)
echo "g2mul,$output" >> benchmark_output/evm.csv

echo "benchmark pairing (2 pairs)"
output=$(PRECOMPILE=pairing INPUT_COUNT=2 ./make_and_bench.sh)
echo "pairing2,$output" >> benchmark_output/evm.csv

echo "benchmark mapfp"
output=$(PRECOMPILE=mapfp ./make_and_bench.sh)
echo "mapfp,$output" >> benchmark_output/evm.csv

echo "benchmark mapfp2"
output=$(PRECOMPILE=mapfp2 ./make_and_bench.sh)
echo "mapfp2,$output" >> benchmark_output/evm.csv
