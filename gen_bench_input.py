import sys, random
random.seed(42)

from bls12_381 import g1_gen_affine, g2_gen_affine, encode_fp_eip2537, encode_fr_eip2537, SUBGROUP_ORDER, g2_gen, g1_gen, g2_gen_mont, g1_gen_mont, to_mont, to_norm, g1_inf

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

def gen_g1_msm_input(num_points):
	input = ""
	for i in range(num_points):
		rand_scalar1 = 0x0fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
		rand_scalar2 = random.randint(0, SUBGROUP_ORDER)
		rand_point = g1_gen().mul(rand_scalar2).to_affine() 

		input += rand_point.encode_eip2537() + encode_fr_eip2537(rand_scalar1)

	return input

def gen_g2_msm_input(num_points):
	input = ""
	for i in range(num_points):
		rand_scalar1 = 0x0fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
		rand_scalar2 = random.randint(0, SUBGROUP_ORDER)
		rand_point = g2_gen().mul(rand_scalar2).to_affine() 

		input += rand_point.encode_eip2537() + encode_fr_eip2537(rand_scalar1)

	return input

def random_g1_point():
	return g1_gen().mul(random.randint(0, SUBGROUP_ORDER)).to_affine().encode_eip2537()

def random_g2_point():
	return g2_gen().mul(random.randint(0, SUBGROUP_ORDER)).to_affine().encode_eip2537()


# return random pairs
# ideally, the inputs will cause the pairing check to pass. However, I haven't figured out how to
# generate worst-case inputs that also pass the pairing check.
def gen_pairing_input(num_pairs: int):
	input = ""
	for i in range(num_pairs):
		pt_g1 = random_g1_point()
		pt_g2 = random_g2_point()
		input += pt_g1 + pt_g2

	return input

# g1 add precompile
if precompile == 'g1add':
	precompile_address = '00'*19 + '0b'
	input_size = encode16byte(256)
	output_size = encode16byte(128)

	g1_add_x = g1_gen().double().to_affine().encode_eip2537()
	g1_add_y = g1_gen().to_affine().encode_eip2537()

	precompile_input = input_size + output_size + precompile_address + g1_add_x + g1_add_y
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

	g2_add_x = g2_gen().double().to_affine().encode_eip2537()
	g2_add_y = g2_gen().to_affine().encode_eip2537()

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
	input = gen_pairing_input(num_pairs)

	precompile_input = input_size + output_size + precompile_address + input
elif precompile == "g1msm":
	if len(sys.argv) < 3:
		raise Exception("need to specify number of points as 2nd parameter")

	num_points = int(sys.argv[2])

	precompile_address = '00'*19 + '0d'
	input_size = encode16byte(num_points * (32 + 128))
	output_size = encode16byte(128)
	input = gen_g1_msm_input(num_points)

	precompile_input = input_size + output_size + precompile_address + input
elif precompile == "g2msm":
	if len(sys.argv) < 3:
		raise Exception("need to specify number of points as 2nd parameter")

	num_points = int(sys.argv[2])

	precompile_address = '00'*19 + '10'
	input_size = encode16byte(num_points * (32 + 256))
	output_size = encode16byte(256)
	input = gen_g2_msm_input(num_points)

	precompile_input = input_size + output_size + precompile_address + input
else:
	raise Exception("invalid precompile selection")


print(precompile_input)
