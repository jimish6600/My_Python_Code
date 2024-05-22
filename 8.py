# default arguments 

def sum(a=1,b=4):
    return a+b

print(sum(b=21))

print(sum(b=3,a=2))

#arbitary arguments

def check(*name):
    for i in range(len(name)):
        print(name[i])


check(1,2,3)