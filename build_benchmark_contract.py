import sys

source_file = sys.argv[1]

loop_body = """
		dup4
		swap1
		dup6
		0x00
		dup6
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
