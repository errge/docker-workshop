def fib(n):
  if n == 0: return 0
  if n == 1: return 1
  return fib(n-1) + fib(n-2)

# Make this work for 100!
print(fib(10))

#with open('template-output.txt', 'r') as f:
#  print(f.read())
