#! /usr/bin/env bash

for precompile in g1add g1mul g2add g2mul mapfp mapfp2
do
	echo "benchmarking $precompile"
	echo -n "	"
	PRECOMPILE=$precompile ./benchmark.sh
done

echo "benchmarking g1msm"
./benchmark_g1msm.sh

echo "benchmarking g2msm"
./benchmark_g2msm.sh

echo "benchmarking pairing"
for input_count in {1..8}
do
	echo -n "	$input_count pairs: "
	PRECOMPILE=pairing INPUT_COUNT=$input_count ./benchmark.sh
done
