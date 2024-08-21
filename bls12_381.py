import copy

SUBGROUP_ORDER = 0x73eda753299d7d483339d80809a1d80553bda402fffe5bfeffffffff00000001
fq_mod = 0x1a0111ea397fe69a4b1ba7b6434bacd764774b84f38512bf6730d2a0f6b0f6241eabfffeb153ffffb9feffffffffaaab
r = 1 << 384
mod_inv = pow(r, -1, fq_mod)
r_squared = (r ** 2) % fq_mod

def mulmont(x, y) -> int:
    return x * y * mod_inv % fq_mod

def to_mont(val):
    return mulmont(val, r_squared)

def to_norm(val):
    return mulmont(val, 1)

def fq_add(x, y) -> int:
    return (x + y) % fq_mod

def fq_sub(x, y) -> int:
    return (x - y) % fq_mod

def fq_mul(x, y) -> int:
    return mulmont(x, y)

def fq_sqr(x) -> int:
    return mulmont(x, x)

def fq_inv(x) -> int:
    # TODO implement this using fermat's little theorem with the generated addchain
    x_norm = to_norm(x)
    res = pow(x, -1, fq_mod)
    return to_mont(res)

def encode_fp_eip2537(x) -> str:
    x_hex = hex(x)[2:]
    return "0" * (128 - len(x_hex)) + x_hex

def encode_fr_eip2537(x) -> str:
    x_hex = hex(x)[2:]
    return "0" * (64 - len(x_hex)) + x_hex

class G1AffinePoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def encode_eip2537(self):
        return encode_fp_eip2537(self.x) + encode_fp_eip2537(self.y)

    def eq(self, other):
        return self.x == other.x and self.y == other.y

class G1ProjPoint:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def from_affine(affine_point):
        return G1ProjPoint(affine_point.x, affine_point.y, to_mont(1))

    def to_affine(self):
        if self.is_inf():
            return G1AffinePoint(0, 0)

        z_inv = fq_inv(self.z)
        return G1AffinePoint(fq_mul(self.x, z_inv), fq_mul(self.y, z_inv))

    def is_on_curve(self):
        # TODO: return Y^2 Z = X^3 + b Z^3
        pass

    def add(self, rhs):
        res = point_add(self, rhs, fq_mul, fq_add, fq_sub, fq_mul_by_3b)
        return G1ProjPoint(res[0], res[1], res[2])

    def double(self):
        res = point_double(self, fq_mul, fq_add, fq_sub, fq_mul_by_3b)
        return G1ProjPoint(res[0], res[1], res[2])

    def is_inf(self):
        pass

def fq2_mul(x, y) -> (int, int):
    t0 = fq_mul(x[0], y[0])
    t1 = fq_mul(x[1], y[1])
    t2 = fq_mul(x[0], y[1])
    t3 = fq_mul(x[1], y[0])

    res = (
        fq_sub(t0, t1),
        fq_add(t2, t3)
    )
    return res

def fq2_mul_by_fq(x, fq_elem):
    return fq_mul(x[0], fq_elem), fq_mul(x[1], fq_elem)

def fq2_inv(x) -> (int, int):
    t0 = fq_sqr(x[0])
    t1 = fq_sqr(x[1])
    t0 = fq_add(t0, t1)
    t0 = fq_inv(t0)
    res_0 = fq_mul(t0, x[0])
    res_1 = fq_sub(0, t0)
    res_1 = fq_mul(x[1], res_1)

    return (
        res_0,
        res_1)

def fq2_add(x, y) -> (int, int):
    res = (
        fq_add(x[0], y[0]),
        fq_add(x[1], y[1]))
    return res

def fq2_sub(x, y) -> (int, int):
    res = (
        fq_sub(x[0], y[0]),
        fq_sub(x[1], y[1]))
    return res

def fq2_mul_by_3b(x):
    # TODO: double-check
    return fq2_mul(x, (to_mont(12), to_mont(12)))

def fq_mul_by_3b(x):
    return fq_mul(x, to_mont(12))

class G2AffinePoint:
    def __init__(self, x0, x1, y0, y1):
        self.x = (x0, x1)
        self.y = (y0, y1)

    def encode_eip2537(self):
        return encode_fp_eip2537(self.x[0]) + encode_fp_eip2537(self.x[1]) + encode_fp_eip2537(self.y[0]) + encode_fp_eip2537(self.y[1])

    def eq(self, other) -> bool:
        return self.x[0] == other.x[0] and self.x[1] == other.x[1] and self.y[0] == other.y[0] and self.y[1] == other.y[1]

class G2ProjPoint:
    def __init__(self, x0, x1, y0, y1, z0, z1):
        self.x = (x0, x1)
        self.y = (y0, y1)
        self.z = (z0, z1)

    def clone(self):
        return copy.deepcopy(self)

    def to_affine(self):
        if self.is_inf():
            return G2AffinePoint(0, 0, 0, 0)
        z_inv = fq2_inv((self.z[0], self.z[1]))
        x = fq2_mul((self.x[0], self.x[1]), z_inv)
        y = fq2_mul((self.y[0], self.y[1]), z_inv)
        return G2AffinePoint(x[0], x[1], y[0], y[1])


    def add(self, rhs):
        res = point_add(self, rhs, fq2_mul, fq2_add, fq2_sub, fq2_mul_by_3b)
        return G2ProjPoint(res[0][0], res[0][1], res[1][0], res[1][1], res[2][0], res[2][1])

    def double(self):
        res = point_double(self, fq2_mul, fq2_add, fq2_sub, fq2_mul_by_3b)
        return G2ProjPoint(res[0][0], res[0][1], res[1][0], res[1][1], res[2][0], res[2][1])

    def mul(self, scalar):
        identity = g2_inf()
        return point_mul(self, scalar, identity, fq2_mul, fq2_add, fq2_sub, fq2_mul_by_3b)

    def is_inf(self):
        return self.x == (0, 0) and self.z == (0, 0) and self.y != (0, 0)

def point_add(self, rhs, f_mul, f_add, f_sub, mul_by_3b):
        # Algorithm 7, https://eprint.iacr.org/2015/1060.pdf

        t0 = f_mul(self.x, rhs.x)
        t1 = f_mul(self.y, rhs.y)
        t2 = f_mul(self.z, rhs.z)
        t3 = f_add(self.x, self.y)
        t4 = f_add(rhs.x, rhs.y)
        t3 = f_mul(t3, t4)
        t4 = f_add(t0, t1)
        t3 = f_sub(t3, t4)
        t4 = f_add(self.y, self.z)
        x3 = f_add(rhs.y, rhs.z)
        t4 = f_mul(t4, x3)
        x3 = f_add(t1, t2)
        t4 = f_sub(t4, x3)
        x3 = f_add(self.x, self.z)
        y3 = f_add(rhs.x, rhs.z)
        x3 = f_mul(x3, y3)
        y3 = f_add(t0, t2)
        y3 = f_sub(x3, y3)
        x3 = f_add(t0, t0)
        t0 = f_add(x3, t0)
        t2 = mul_by_3b(t2)
        z3 = f_add(t1, t2)
        t1 = f_sub(t1, t2)
        y3 = mul_by_3b(y3)
        x3 = f_mul(t4, y3)
        t2 = f_mul(t3, t1)
        x3 = f_sub(t2, x3)
        y3 = f_mul(y3, t0)
        t1 = f_mul(t1, z3)
        y3 = f_add(t1, y3)
        t0 = f_mul(t0, t3)
        z3 = f_mul(z3, t4)
        z3 = f_add(z3, t0)

        return (x3, y3, z3)

def point_double(self, f_mul, f_add, f_sub, mul_by_3b):
        # Algorithm 9, https://eprint.iacr.org/2015/1060.pdf
        t0 = f_mul(self.y, self.y)
        z3 = f_add(t0, t0)
        z3 = f_add(z3, z3)
        z3 = f_add(z3, z3)
        t1 = f_mul(self.y, self.z)
        t2 = f_mul(self.z, self.z)
        t2 = mul_by_3b(t2)
        x3 = f_mul(t2, z3)
        y3 = f_add(t0, t2)
        z3 = f_mul(t1, z3)
        t1 = f_add(t2, t2)
        t2 = f_add(t1, t2)
        t0 = f_sub(t0, t2)
        y3 = f_mul(t0, y3)
        y3 = f_add(x3, y3)
        t1 = f_mul(self.x, self.y)
        x3 = f_mul(t0, t1)
        x3 = f_add(x3, x3)

        return (x3, y3, z3)

def point_mul(point, scalar, identity, f_mul, f_add, f_sub, mul_by_3b):
        # scalar bits from most to least significant
        scalar_bits = [scalar >> i & 1 for i in range(scalar.bit_length() - 1,-1,-1)]

        res = identity.clone()

        for bit in scalar_bits:
                res = res.double()
                if bit == 1:
                        res = point.add(res)

        return res

def g2_point_from_raw(raw):
    return G2ProjPoint(to_norm(int(raw[0:96], 16)),
    to_norm(int(raw[96:192], 16)),
    to_norm(int(raw[192:288], 16)),
    to_norm(int(raw[288:384], 16)),
    to_norm(int(raw[384:480], 16)),
    to_norm(int(raw[480:576], 16)))
    
g1_gen_x = 3685416753713387016781088315183077757961620795782546409894578378688607592378376318836054947676345821548104185464507
g1_gen_y = 1339506544944476473020471379941921221584933875938349620426543736416511423956333506472724655353366534992391756441569
g1_gen_point = G1ProjPoint(g1_gen_x, g1_gen_y, 1)
g1_gen_point_affine = G1AffinePoint(g1_gen_x, g1_gen_y)

g2_gen_x_0 = 352701069587466618187139116011060144890029952792775240219908644239793785735715026873347600343865175952761926303160
g2_gen_x_1 = 3059144344244213709971259814753781636986470325476647558659373206291635324768958432433509563104347017837885763365758
g2_gen_y_0 = 1985150602287291935568054521177171638300868978215655730859378665066344726373823718423869104263333984641494340347905
g2_gen_y_1 = 927553665492332455747201965776037880757740193453592970025027978793976877002675564980949289727957565575433344219582
g2_gen_z_0 = 1
g2_gen_z_1 = 0

g2_gen_point = G2ProjPoint(g2_gen_x_0, g2_gen_x_1, g2_gen_y_0, g2_gen_y_1, g2_gen_z_0, g2_gen_z_1)
g2_gen_point_affine = G2AffinePoint(g2_gen_x_0, g2_gen_x_1, g2_gen_y_0, g2_gen_y_1)


def g1_gen():
    return g1_gen_point

def g1_gen_mont():
    res = g1_gen()
    res.x = to_mont(res.x)
    res.y = to_mont(res.y)
    res.z = to_mont(res.z)
    return res

def g2_gen():
    return g2_gen_point.clone()

def g2_inf():
    return G2ProjPoint(0, 0, to_mont(1), to_mont(1), 0, 0)

def g2_gen_mont():
    res = g2_gen()
    res.x = (to_mont(res.x[0]),to_mont(res.x[1]))
    res.y = (to_mont(res.y[0]),to_mont(res.y[1]))
    res.z = (to_mont(res.z[0]),to_mont(res.z[1]))
    return res


def g2_gen_affine():
    return g2_gen_point_affine

def g1_gen_affine():
    return g1_gen_point_affine

def test_g2_mul():
    gen = g2_gen_mont()

    scalar = 2
    res = gen.mul(scalar)
    expected = gen.add(gen)
    assert res.to_affine().eq(expected.to_affine())

    scalar = 3
    res = gen.mul(scalar)
    expected = gen.add(gen).add(gen)
    assert res.to_affine().eq(expected.to_affine())

    scalar = SUBGROUP_ORDER
    res = gen.mul(scalar)
    assert res.is_inf()

def test_g2_add():
    gen = g1_gen_mont()
    res = gen.add(gen)
    #res = gen.double()

def run_tests():
    test_g2_mul()
    #test_g2_add()

if __name__ == "__main__":
    run_tests()
    print("success")
