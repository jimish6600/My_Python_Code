a = [1,2,3,4,5,6,6,5,4,3,2,1]

for i in range(len(a)):
    print(a[i], end=" ")
print()
for i,v in enumerate(a):
    print(f"{i} : {v}")