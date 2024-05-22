l = [1,4,2,5,7,2]
l.sort()
print(l)

l.sort(reverse=True)
print(l)
m = l.copy()

m[0]=0
l.insert(1,10)
print(l)# if we make copy list didn't change


# tuple
tup = (1,2,3)
print(tup)

print(dir(l))