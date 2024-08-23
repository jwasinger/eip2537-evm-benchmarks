import sys

source_file = sys.argv[1]

# stack: return offset, loop counter, precompile_address, output_size, input_size
# want: gas	addr	argsOffset	argsLength	retOffset	retLength
loop_body = """
		dup4
		dup2
		dup7
		0x00
		dup7
		gaslimit
		staticcall
		pop
"""

# TODO: will want to parameterize this based on expected runtime
loop_size = 1

with open(source_file) as f:
	lines = f.readlines()
	for line in lines:
		line = line.strip('\n')
		if line == "replaceme":
			for i in range(loop_size):
				print(loop_body)
		else:
			print(line)
