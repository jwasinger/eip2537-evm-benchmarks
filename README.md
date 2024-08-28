# EIP-2537 Benchmarks

This is a set of cross-client benchmarks for EIP-2537 implemented as a contract which calls a target precompile with worst-case inputs many times.  These are currently executed with Geth' `evm` tool. The next step is to convert them to state tests and execute them across all clients.

Benchmark inputs are based on identified worst-case inputs for the [gnark](https://github.com/Consensys/gnark-crypto/tree/master/ecc/bls12-381) bls12381 implementation used by Geth.

## Usage

Benchmark contracts are written in [huff](https://github.com/huff-language/huff-rs).  To build them `huffc` must be on the executable path.

### Build Benchmarks and Generate Inputs
`./build_benchmarks.sh`

### Run Benchmarks
#### Run All Benchmarks
`GETH_EVM=/path/to/geth/evm/binary ./benchmark_all.sh`

#### Single Benchmark
`GETH_EVM=/path/to/geth/evm/binary PRECOMPILE=pairing INPUT_COUNT=$input_count ./benchmark.sh`

`PRECOMPILE` must be one of `g1add`, `g1mul`, `g1msm`, `g2add`, `g2mul`, `g2msm`, `pairing`, `mapfp`, `mapfp2`.

`INPUT_COUNT` must be specified for g1msm, g2msm, pairing precompiles.  For msm precompiles it can be from 1-32.  For pairing, 1-8.

## Benchmark Inputs:
* G1Add: Input is `2G1 + G1`
* G2 Add: Input is `2G2 + G2`
* G1/G2 Mul: Generator point with a scalar identified to cause close-to-maximum doublings and additions for an implementation GLV 2x scalar decomposition, window size of 2.
* G1/G2 MSM: pairs of random scalars/points within the target subgroup.
* Pairing: pairs of Random points within the target subgroup.
* Fp/Fp2 Mapping: random scalar.  The implementation is assumed to be mostly constant-time.

### Note on MSM
Random inputs are not necessarily the worst-case input. However, they perform poorly with the current gas schedule when limited to single-threaded execution.  For Geth, picking an MSM algorithm that performs best on a single thread and/or modifying the gas schedule of the EIP is a TODO.

## Benchmark Method

The benchmarking contract consists of 2850 static calls to a target precompile contract.  To account for the skew of the overhead from non-precompile EVM instructions, a "no-op" benchmark consisting of 2850 calls to the identity precompile (copying zero bytes) is performed.  The gas and execution time from the no-op benchmark are subtracted from those of the BLS precompile benchmark, before computing the resulting gas rate per precompile operation.

## Geth EVM Benchmark Results on an M2 Macbook Pro

Several benchmark presets were executed and results are included in this repository:
* [EVM benchmarks](benchmark_output/mbp_m2_16gb.txt).
* [EVM benchmarks](benchmark_output/mbp_m2_16gb-no-concurrent.txt) restricted to make MSM non-concurrent
* Native Golang EIP-2537 benchmarks from Geth [here](benchmark_output/geth-native.txt).  Note that provided MSM benchmarks are for 16 points.

Takeaways:
* MSM precompiles are underpriced compared other precompiles, especially when concurrency is disabled.
* Native Go benchmark performance is on par with results calculated from EVM Benchmarks.
	* The G1/G2Add EVM benchmarks have 10, 16% higher reported gas rate than native counterparts.  I'm not yet sure why.
