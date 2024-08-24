import sys

lines = sys.stdin.readlines()

exec_time = 0
gas_used = 0

for line in lines:
	if "execution time:" in line:
		exec_time = line.strip('execution time:  ').rstrip('\n')
		if exec_time.endswith("ms"):
			exec_time = int(float(exec_time[:-2]) * 1000000)
		elif exec_time.endswith("\\xc2\\xb5s"):
			exec_time = int(float(exec_time[:-9]) * 1000)
		elif exec_time.endswith("s"):
			exec_time = int(float(exec_time[:-1]) * 1000000 * 1000)
		else:
			raise Exception("unknown timestamp ending: {}".format(exec_time))
	elif "EVM gas used:" in line:
		gas_used = int(line.strip("EVM gas used:").strip('\\n'))

gas_throughput = gas_used / (exec_time / 1e9)
gas_throughput /= 1e6
print("throughput: {} million gas / sec".format(gas_throughput))
