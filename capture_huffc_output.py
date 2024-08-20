import sys

for line in sys.stdin:
	if "runtime:" in line:
		print(line[9:])
