import sys

from bls12_381 import g1_gen_affine, g2_gen_affine, encode_fp_eip2537, encode_fr_eip2537, SUBGROUP_ORDER, g2_gen, g1_gen, g2_gen_mont, g1_gen_mont, to_mont, to_norm

from glv import high_arity_scalar

# encode-val to 16byte padded big-endian hex string
def encode16byte(val: int):
    val_hex = hex(val)[2:]
    if len(val_hex) % 2 != 0:
        val_hex = "0"+val_hex

    padding = 32 - len(val_hex)
    return "0" * padding + val_hex 

precompile_input = ""
precompile = sys.argv[1]

def gen_pairing_input(num_pairs: int):
	if num_pairs % 2 == 0:
		for i in range(num_pairs):
			if i % 2 == 0:
				pt_g1 = g1_gen().double().to_affine().encode_eip2537()
				pt_g2 = g2_gen().double().neg().to_affine().encode_eip2537()

# g1 add precompile
if precompile == 'g1add':
	precompile_address = '00'*19 + '0b'
	input_size = encode16byte(256)
	output_size = encode16byte(128)

	g2_add_x = g1_gen_mont().double().to_affine().encode_eip2537()
	g2_add_y = g1_gen_mont().to_affine().encode_eip2537()

	precompile_input = input_size + output_size + precompile_address + g2_add_x + g2_add_y
elif precompile == 'g1mul':
	precompile_address = '00'*19 + '0c'
	input_size = encode16byte(128 + 32)
	output_size = encode16byte(128)

	point = g1_gen().double().to_affine().encode_eip2537()
	scalar = encode_fr_eip2537(high_arity_scalar)

	precompile_input = input_size + output_size + precompile_address + point + scalar
elif precompile == 'g2add':
	precompile_address = '00'*19 + '0e'
	input_size = encode16byte(512)
	output_size = encode16byte(256)

	g2_add_x = g2_gen_mont().to_affine().encode_eip2537()
	g2_add_y = g2_gen_mont().to_affine().encode_eip2537()

	precompile_input = input_size + output_size + precompile_address + g2_add_x + g2_add_y
elif precompile == 'g2mul':
	precompile_address = '00'*19 + '0f'
	input_size = encode16byte(256 + 32)
	output_size = encode16byte(256)

	point = g2_gen().double().to_affine().encode_eip2537()
	scalar = encode_fr_eip2537(high_arity_scalar)

	precompile_input = input_size + output_size + precompile_address + point + scalar
elif precompile == "mapfp":
	precompile_address = '00'*19 + '12'
	input_size = encode16byte(64)
	output_size = encode16byte(128)

	fp = encode_fp_eip2537(SUBGROUP_ORDER)

	precompile_input = input_size + output_size + precompile_address + fp
elif precompile == "mapfp2":
	precompile_address = '00'*19 + '13'
	input_size = encode16byte(128)
	output_size = encode16byte(256)

	fp_0 = encode_fp_eip2537(SUBGROUP_ORDER)
	fp_1 = encode_fp_eip2537(SUBGROUP_ORDER)

	precompile_input = input_size + output_size + precompile_address + fp_0 + fp_1
elif precompile == "pairing":
	if len(sys.argv) < 3:
		raise Exception("need to specify number of pairs as 2nd parameter")

	num_pairs = int(sys.argv[2])

	precompile_address = '00'*19 + '11'
	input_size = encode16byte(num_pairs * (128 + 256))
	output_size = encode16byte(32)
	input = ""

	# if num_pairs % 2 == 0: (-2g1, 2G2), (2g1, -2G2) * (-2g1, 2G2), (2g1, -2G2) * ...
	# if num_pairs %2 != 0: (-4
	for i in range(num_pairs):
		if i % 2 == 0:
			pt_g1 = g1_gen().double().neg().to_affine().encode_eip2537()
			pt_g2 = g2_gen().to_affine().encode_eip2537()
			input += pt_g1 + pt_g2
		else:
			pt_g1 = g1_gen().double().to_affine().encode_eip2537()
			pt_g2 = g2_gen().to_affine().encode_eip2537()
			input += pt_g1 + pt_g2

	precompile_input = input_size + output_size + precompile_address + input
else:
	raise Exception("invalid precompile selection")


print(precompile_input)
