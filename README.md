# EIP-2537 Benchmarks

This is a set of cross-client benchmarks for EIP-2537 implemented as a contract which calls a target precompile with worst-case inputs many times.  When the spec for Prague becomes finalized, these will be turned into state tests so that they can easily be ran by various clients.

Benchmark inputs are based on identified worst-case inputs for the [gnark](https://github.com/Consensys/gnark-crypto/tree/master/ecc/bls12-381) bls12381 implementation used by Geth.

## Usage

Benchmark contracts are written in [huff](https://github.com/huff-language/huff-rs).  To build them `huffc` must be on the executable path.

Build and run benchmarks:  `GETH_EVM=/path/to/geth/evm/binary PRECOMPILE=precompileName INPUT_COUNT=1234 ./make_and_bench.sh`

`PRECOMPILE` must be one of `g1add`, `g1mul`, `g1msm`, `g2add`, `g2mul`, `g2msm`, `pairing`, `mapfp`, `mapfp2`.

For `pairing`, `g1msm`, `g2msm`: `INPUT_COUNT` must be provided to specify the number of inputs (points or pairs depending on the precompile).

## Benchmark Inputs:
* G1Add: Input is `2G1 + G1`
* G2 Add: Input is `2G2 + G2`
* G1/G2 Mul: Generator point with a scalar identified to cause close-to-maximum doublings and additions for an implementation that performs a 2-bit windowed GLV.
* G1/G2 MSM: Random scalars and points within the target subgroup.
* Pairing: Random points within the target subgroup.
* Fp/Fp2 Mapping: random scalar.  The implementation is assumed to be mostly constant-time.

### Note on MSM
Random inputs are not necessarily the worst-case input. However, they perform poorly with the current gas schedule when limited to single-threaded execution.  For Geth, picking an MSM algorithm that performs best on a single thread and/or modifying the gas schedule of the EIP is a TODO.
