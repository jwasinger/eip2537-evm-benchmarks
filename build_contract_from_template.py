import sys

source_file = sys.argv[1]

# stack: return offset, loop counter, precompile_address, output_size, input_size
# want: gas	addr	argsOffset	argsLength	retOffset	retLength
bench_loop_body = """
		dup4
		dup2
		dup7
		0x00
		dup7
		gaslimit
		staticcall
		pop
"""

noop_loop_body = """
		0x00
		0x00
		0x00
		0x00
		0x04
		gaslimit
		staticcall
		pop
"""

# TODO: will want to parameterize this based on expected runtime
loop_size = 2850

loop_body = ""
if sys.argv[2] == 'bench':
	loop_body = bench_loop_body
elif sys.argv[2] == 'noop':
	loop_body = noop_loop_body

loop_size = int(sys.argv[3])

with open(source_file) as f:
	lines = f.readlines()
	for line in lines:
		line = line.strip('\n')
		if line == "replaceme":
			for i in range(loop_size):
				print(loop_body)
		else:
			print(line)
