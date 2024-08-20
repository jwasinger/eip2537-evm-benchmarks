# EIP-2537 Benchmarks

This is a set of cross-client benchmarks for EIP-2537 implemented as a set of EVM bytecodes.

Benchmarks:
G1 Add (done): any valid, non-infinite input is worst-case (assuming inversion is roughly constant-time)
G2 Add: any valid, non-infinite input is worst-case (assuming inversion is roughly constant-time)
G1 Mul: Any valid non-infinite input that doesn't produce infinite result where the decomp of the scalar s1|s2 is all ones.
G2 Mul: Any valid non-infinite input that doesn't produce infinite result where the decomp of the scalar s1|s2 is all ones.

Pairing: constant-time operation.  any valid input is a worst-case input.
* bench for 1 pair, 2 pairs, 3 pairs, ...

Fp/Fp2 Mapping: most inputs should be worst-case (but need to verify this)

MSM: ?

## Usage
`PRECOMPILE=precompileName ./make_and_bench.sh`
currently supports "g1add", "g2add" for `PRECOMPILE` values.
