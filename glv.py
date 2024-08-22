import random

from bls12_381 import G2ProjPoint, fq2_mul_by_fq, g2_gen_mont, SUBGROUP_ORDER, to_mont, to_norm

class Lattice():
	def __init__(self, v1: (int, int), v2: (int, int), b1: int, b2: int, n: int):
		self.v1 = v1
		self.v2 = v2
		self.b1 = b1
		self.b2 = b2

		# n = 2 * uint(((det.BitLen()+32)>>6)<<6)
		self.n = n


def get_vector(v1: (int, int), v2: (int, int), a: int, b: int) -> (int, int):
	tmp = b * v2[0]
	res0 = a * v1[0] + tmp
	res1 = a * v1[1] + tmp
	return res0, res1

def split_scalar(s: int, l: Lattice):
	k1 = s * l.b1
	k2 = s * l.b2

	k1 = k1 >> l.n
	k2 = k2 >> l.n

	v0, v1 = get_vector(l.v1, l.v2, k1, k2)

	v0 = s - v0
	v1 = - v1
	return v0, v1

def bls12381_lattice() -> Lattice:
	# TODO: ensure these are not in montgomery form (b1, b2)
	v1 = (228988810152649578064853576960394133503  ,  -1)
	v2 = (1, 228988810152649578064853576960394133504)
	b1=58552240701214274452021999096850125581542494224669441691648594964201968916268199467788850628613995194398422433283175
	b2=-255699135089535202043525422716183576215815630510683217819334674386498370757523
	n=512

	return Lattice(v1, v2, b1, b2, n)

def phi(p: G2ProjPoint) -> G2ProjPoint:
	res = p.clone()

	# fq elem (montgomery form)
	third_root_one_g2 = 786190290886016440328299728779656453203981590080344581554777668754318906274739675415266862557957487153214149780712

	res.x = fq2_mul_by_fq((res.x[0], res.x[1]), third_root_one_g2)
	return res

def mul_glv(p: G2ProjPoint, s: int) -> G2ProjPoint:
	lattice = bls12381_lattice()

	table = [None]*16
	table[0] = p.clone()
	table[3] = phi(p)

	k = split_scalar(s, lattice)
	if k[0] < 0:
		k0 = -k0
		table[0] = table[0].neg()

	if k[1] < 0:
		k1 = -k1
		table[3] = table[3].neg()

	table[1] = table[0].double()
	table[2] = table[1].add(table[0])
	table[3] = table[3].add(table[0])
	table[5] = table[3].add(table[1])
	table[6] = table[3].add(table[2])
	table[7] = table[3].double()
	table[8] = table[7].add(table[0])
	table[9] = table[7].add(table[1])
	table[10] = table[7].add(table[2])
	table[11] = table[7].add(table[3])
	table[12] = table[11].add(table[0])
	table[13] = table[11].add(table[1])
	table[14] = table[11].add(table[2])

	# TODO: set k0_bytes, k1_bytes

	max_bit_len = max(len(k0_bytes), len(k1_bytes))
	hi_word_idx = (max_bit_len - 1) // 64

	# TODO: set k1_words, k2_words

	for i in range(0, hi_word_idx, -1):
		u64_mask = 3 << 62
		for j in range(32):
			res = res.double().double()
			b1 = (k1[i] & mask) >> (62 - 2 * j)
			b2 = (k2[i] & mask) >> (62 - 2 * j)

			if b1|b2 != 0:
				s = b2<<2 | b1
				res = res.Add(table[s-1])

	return res

def check_arity(x, y):
	max_val = max(x,y)
	arity = 0
	for i in range(0, len(bin(max_val)) - 2, 2):
		bits_x = x & 0b11
		bits_y = y & 0b11
		if bits_x | bits_y:
			arity += 1

		x >>= 2
		y >>= 2
	return arity

def find_scalars_with_high_arity():
	lattice = bls12381_lattice()

	best_scalar = 0
	best_arity = 0
	best_total_length = 0

	while True:
		scalar = random.randint(0, SUBGROUP_ORDER)
		k = split_scalar(scalar, lattice)
		arity = check_arity(k[0], k[1])
		total_length = len(bin(max(k[0], k[1]))) - 2
		if arity > best_arity and total_length > best_total_length:
			best_scalar = scalar
			best_total_length = total_length
			best_arity = arity

			print(best_scalar)
			print(best_arity)
			print(best_total_length)
			print()

# scalar where the decomposition has 62 "double-bits" (sliding window of size 2) of arity (s1|s2 not equal to zero for any bit-pairs at bits [0,2], [2,4], etc.)
high_arity_scalar = 50597600879605352240557443896859274688352069811191692694697732254669473040618

def main():
	lattice = bls12381_lattice()
	#point = g2_gen_mont()
	#s = SUBGROUP_ORDER

	#res = mul_glv(point, s)


	k = split_scalar(high_arity_scalar, lattice)
	import pdb; pdb.set_trace()

if __name__ == "__main__":
	main()
