import sys

class stdout2str:
	def __init__(self):
		self.s = ""
	def write(self, buf):
		self.s += buf

def runFun(function_name):
	tempout = sys.stdout
	out = stdout2str()
	sys.stdout = out
	exec("temp_ret = %s"%(function_name))
	sys.stdout = tempout
	print "catch",temp_ret, out.s

def fun():
	print "hello world"
	return 2046

if __name__ == '__main__':
	function_name = "fun()"
	runFun(function_name)