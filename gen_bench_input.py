import sys

from bls12_381 import g1_gen_affine, g2_gen_affine

# encode-val to 16byte padded big-endian hex string
def encode16byte(val: int):
    val_hex = hex(val)[2:]
    if len(val_hex) % 2 != 0:
        val_hex = "0"+val_hex

    padding = 32 - len(val_hex)
    return "0" * padding + val_hex 

precompile_input = ""
precompile = sys.argv[1]

# g1 add precompile
if precompile == 'g1add':
	precompile_address = '00'*19 + '0b'
	input_size = encode16byte(256)
	output_size = encode16byte(128)

	g2_add_x = g1_gen_affine().encode_eip2537()
	g2_add_y = g1_gen_affine().encode_eip2537()

	precompile_input = input_size + output_size + precompile_address + g2_add_x + g2_add_y
elif precompile == 'g2add':
	precompile_address = '00'*19 + '0e'
	input_size = encode16byte(512)
	output_size = encode16byte(256)

	g2_add_x = g2_gen_affine().encode_eip2537()
	g2_add_y = g2_gen_affine().encode_eip2537()

	precompile_input = input_size + output_size + precompile_address + g2_add_x + g2_add_y
else:
	raise Exception("invalid precompile selection")


print(precompile_input)
