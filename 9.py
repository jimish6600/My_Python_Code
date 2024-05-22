l = [1,2,3,"r"]
l.append(4)
print(l)
print(l[0])
print(l[1])
print(l[2])

if 2 in l:
    print("yes")

print(l[1:-1])

lis = [i**i for i in range(10) if i%2==0]

print(lis)