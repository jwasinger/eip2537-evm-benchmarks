import math
import os
import random
import sys
import subprocess
import tempfile

import numpy as np

EVMMAX_ARITH_ITER_COUNT = 1

MAX_LIMBS = 12

EVMMAX_ARITH_OPS = {
    "addmodx": "c3",
    "submodx": "c4",
    "mulmodx": "c5",
}

LIMB_SIZE = 8

OP_SETMOD = "c0"
OP_STOREX = "c2"

EVM_OPS = {
    "POP": "50",
    "MSTORE": "52",
}

def reverse_endianess(word: str):
    assert len(word) == LIMB_SIZE * 2, "invalid length"

    result = ""
    for i in reversed(range(0, len(word), 2)):
        result += word[i:i+2]
    return result

def calc_limb_count(val: int) -> int:
    assert val > 0, "val must be greater than 0"

    count = 0
    while val != 0:
        val >>= 64
        count += 1
    return count

def encode_val_for_mstore(val: int, res_size: int) -> [str]:
    # modulus:
    #   * assert that it fills most significant limb
    #   less than evm word size:
    #       * right-pad the hex literal to become evm word size
    #   greater than evm word size:
    #       * right-pad the hex literal to become multiple of evm word size
    # value:
    #   * left-pad until it is res_size
    #   * right pad until it is a multiple of evm word size
    pass

def encode_modulus_for_mstore(mod: int) -> [str]:
    # TODO: assert that it would fill most significant u64 limb
    mod_hex = hex(mod)[2:]
    if len(mod_hex) % 2 != 0:
        mod_hex = "0"+mod_hex

    if len(mod_hex) % 64 != 0:
        padded_size = ((len(mod_hex) + 63) // 64) * 64
        mod_hex = mod_hex + "0"*(padded_size  - len(mod_hex))

    res = []
    for i in range(0, len(mod_hex), 64):
        res.append(mod_hex[i:i+64])

    return res

def encode_field_element_for_mstore(val: int, res_size: int) -> [str]:
    if val == 0:
        return ['00']

    val_hex = hex(val)[2:]
    if len(val_hex) % 2 != 0:
        val_hex = "0"+val_hex

    if len(val_hex) // 2 < res_size:
        pad_size = res_size * 2 - len(val_hex)
        val_hex = "0"*pad_size + val_hex

    if len(val_hex) % 64 != 0:
        padded_size = ((len(val_hex) + 63) // 64) * 64
        val_hex = val_hex + "0"*(padded_size  - len(val_hex))

    res = []
    for i in range(0, len(val_hex), 64):
        res.append(val_hex[i:i+64])

    return res

def gen_push_int(val: int) -> str:
    assert val >= 0 and val < (1 << 256), "val must be in acceptable evm word range"

    literal = hex(val)[2:]
    if len(literal) % 2 == 1:
        literal = "0" + literal
    return gen_push_literal(literal)

def gen_push_literal(val: str) -> str:
    assert len(val) <= 64, "val is too big"
    assert len(val) % 2 == 0, "val must be even length"
    push_start = 0x60
    push_op = hex(push_start - 1 + int(len(val) / 2))[2:]

    assert len(push_op) == 2, "bug"

    return push_op + val

def gen_mstore_int(offset: int, val: int) -> str:
    return gen_push_int(offset) + gen_push_int(val) + EVM_OPS["MSTORE"]

def gen_mstore_literal(val: str, offset: int) -> str:
    return gen_push_literal(val) + gen_push_int(offset) + EVM_OPS["MSTORE"]

def reverse_endianess(val: str):
    assert len(val) % 2 == 0, "must have even string"
    result = ""
    for i in reversed(range(0, len(val), 2)):
        result += val[i:i+2]

    return result

def gen_random_val(modulus: int) -> int:
    return random.randrange(0, modulus)

def calc_field_elem_size(mod: int) -> int:
    mod_byte_count = int(math.ceil(len(hex(mod)[2:]) / 2))
    mod_u64_count = (mod_byte_count + 7) // 8
    return mod_u64_count * 8

def gen_random_scratch_space(dst_mem_offset: int, mod: int, scratch_count: int) -> str:
    field_elem_size = calc_field_elem_size(mod)
    # allocate the scratch space: store 0 at the last byte
    res = gen_mstore_int(dst_mem_offset + field_elem_size * scratch_count, 0)

    for i in range(scratch_count):
        res += gen_mstore_field_elem(dst_mem_offset + i * field_elem_size, gen_random_val(mod), field_elem_size)

    return res


# store a 64bit aligned field element (size limb_count * 8 bytes) in big-endian
# repr to EVM memory
def gen_mstore_field_elem(dst_offset: int, val: int, field_width_bytes: int) -> str:
    evm_words = encode_field_element_for_mstore(val, field_width_bytes)
    result = ""
    offset = dst_offset
    for word in evm_words:
        result += gen_mstore_literal(word, offset)
        offset += 32

    return result

def gen_mstore_modulus(dst_offset, mod: int) -> str:
    evm_words = encode_modulus_for_mstore(mod)
    result = ""
    offset = dst_offset
    for word in evm_words:
        result += gen_mstore_literal(word, offset)
        offset += 32

    return result

def gen_storex(dst_slot: int, src_offset: int, count: int) -> str:
    return  gen_push_int(count) + gen_push_int(src_offset) + gen_push_int(dst_slot) + OP_STOREX


def size_bytes(val: int) -> int:
    val_hex = hex(val)[2:]
    if len(val_hex) % 2 != 0:
        val_hex = '0'+val_hex
    return len(val_hex) // 2

def gen_encode_arith_immediate(out, x, y) -> str:
    result = ""
    for b1 in [out, x, y]:
        assert b1 >= 0 and b1 < 256, "argument must be in byte range"

        b1 = hex(b1)[2:]
        if len(b1) == 1:
            b1 = '0'+b1

        result += b1
    return result

def encode_single_byte(val: int) -> str:
    assert val < 256, "val mus tbe representable as a byte"
    result = hex(val)[2:]
    if len(result) == 1:
        result = '0' + result
    return result

SCRATCH_SPACE_SIZE=256
def gen_setmod(mod: int) -> str:
    mod_size = size_bytes(mod)
    field_elem_size = calc_field_elem_size(mod)

    result = gen_mstore_modulus(0, mod) # store big-endian modulus to memory at offset 0

    result += gen_push_int(SCRATCH_SPACE_SIZE) # scratch space field element count
    result += gen_push_int(mod_size) # mod size
    result += gen_push_literal(encode_single_byte(0)) # source offset for modulus
    result += gen_push_int(0) # mod-id, not used
    result += OP_SETMOD 
    return result

def gen_arith_op(op: str, out_slot: int, x_slot: int, y_slot: int) -> str:
    return EVMMAX_ARITH_OPS[op] + gen_encode_arith_immediate(out_slot, x_slot, y_slot)

MAX_CONTRACT_SIZE = 24576


def gen_benchmark(op: str, mod: int):
    bench_code = ""

    # setmod
    bench_code += gen_setmod(mod)

    # store inputs
    bench_code += gen_random_scratch_space(0, mod, SCRATCH_SPACE_SIZE)

    # storex
    bench_code += gen_storex(0, 0, SCRATCH_SPACE_SIZE)

    # loop

    arr = np.array([i for i in range(SCRATCH_SPACE_SIZE)])
    p1 = np.random.permutation(arr)
    p2 = np.random.permutation(arr)
    p3 = np.random.permutation(arr)

    scratch_space_vals = [(p1[i], p2[i], p3[i]) for i in range(len(arr))]
    # TODO: generate the calls
    iter_count = 5000

    inner_loop_arith_op_count = 0
    loop_body = ""

    for i in range(iter_count):
        loop_body += gen_arith_op(op, p1[i % len(arr)], p2[i % len(arr)], p3[i % len(arr)])
        inner_loop_arith_op_count += 1

    bench_code = gen_loop().format(bench_code, loop_body, gen_push_int(int(len(bench_code) / 2) + 33))
    return bench_code, inner_loop_arith_op_count * 256 

# bench some evm bytecode and return the runtime in ns

def gen_loop() -> str:
    return "{}7fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff015b{}60010180{}57"

def bench_geth(code_file: str) -> int:
    geth_path = "go-ethereum/build/bin/evm"
    if os.getenv('GETH_EVM') != None:
        geth_path = os.getenv('GETH_EVM')

    geth_exec = os.path.join(os.getcwd(), geth_path)
    geth_cmd = "{} --codefile {} --bench run".format(geth_exec, code_file)
    result = subprocess.run(geth_cmd.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise Exception("geth exec error: {}".format(result.stderr))

    exec_time = str(result.stderr).split('\\n')[1].strip('execution time:  ')

    if exec_time.endswith("ms"):
        exec_time = int(float(exec_time[:-2]) * 1000000)
    elif exec_time.endswith("s"):
        exec_time = int(float(exec_time[:-1]) * 1000000 * 1000)
    else:
        raise Exception("unknown timestamp ending: {}".format(exec_time))

    return exec_time

LOOP_ITERATIONS = 255

# return a value between [1<<min_size_bits, 1<<max_size_bits)
def gen_random_mod(min_size_bits: int, max_size_bits: int):
   while True:
       # TODO: this will generate moduli that skew towards occupying the most significant bit
       # will want to test with more varied inputs
        candidate = random.randrange(1 << min_size_bits, 1 << max_size_bits)
        if candidate % 2 != 0:
            return candidate

def generate_and_run_benchmark(arith_op_name: str, mod: int) -> (int, int):
    bench_code, evmmax_op_count = gen_benchmark(arith_op_name, mod)
    return bench_geth(bench_code), evmmax_op_count

def bench_run(benches):
    for op_name, limb_count_min, limb_count_max in benches:
        for i in range(limb_count_min, limb_count_max + 1):
            evmmax_bench_time, evmmax_op_count = bench_geth_evmmax(op_name, i) 

            setmod_est_time = 0

            est_time = math.ceil((evmmax_bench_time) / (evmmax_op_count * LOOP_ITERATIONS))
            print("{},{},{}".format(op_name, limb_count, est_time))

def bench_range(min_limbs, max_limbs):
    for arith_op_name in ["addmodx", "submodx", "mulmodx"]:
        #TODO: make this loop test the lowest limb count
        for limb_count in range(min_limbs, max_limbs + 1):
            mod = gen_random_mod((limb_count - 1) * 8 * 8 + 1, (limb_count) * 8 * 8)
            bench_code, arith_op_count = gen_benchmark(arith_op_name, mod)
            fp = tempfile.NamedTemporaryFile()#"bench_codes/{}-{}.hex".format(arith_op_name, hex(mod)[2:12])
            fp.write(bytes(bench_code, 'utf-8'))

            BENCH_REPEAT=1
            for i in range(BENCH_REPEAT):
                bench_time = bench_geth(fp.name) 

                prefix = ''
                if os.getenv('PRESET') != None:
                    prefix = os.getenv('PRESET')
                print("{},{},{},{}".format(prefix, arith_op_name, limb_count, round(bench_time / arith_op_count)))

if __name__ == "__main__":
    random.seed(42)
    if len(sys.argv) == 1:
        bench_range(1, 12)
    elif len(sys.argv) >= 2:
        bench_range(int(sys.argv[1]), int(sys.argv[2]))
    else:
        print("too many args")
