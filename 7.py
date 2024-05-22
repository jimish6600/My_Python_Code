name = "jimish"

for i in name:
    print(i,end=" ")

for i in range(1,10):
    print(i)

i = 10

while(i>0):
    print(i)
    i-=1

for i in range(10):
    
    if(i==2):
        continue
    if(i==5):
        break
    print(i)