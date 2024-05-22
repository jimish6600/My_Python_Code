sum = lambda a,b=2: a+b

print(sum(1,2))

l = [3,3,3,3,3,3,3]

ans = list(map(sum,l)) 

print(ans)

def check(a):
    return a<4
nans = list(filter(check,ans))

print(nans)

