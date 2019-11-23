import sys

testInput = "a=5\nb=3"
source = "print(a+b)"
f = open('test.txt', 'w')
f.write(testInput+'\n')
f.write(source)
f.close()

f = open('test.txt', 'r')
f2 = open('realResult.txt', 'w')
text_str = f.read()
stdout = sys.stdout
sys.stdout = f2
code = compile(text_str, 'text.txt', 'exec')
exec(text_str)
f2.close()
sys.stdout= stdout


