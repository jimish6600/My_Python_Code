import os

if( not os.path.exists('data')):
    os.mkdir("data")
 
for i in range(100):
    os.mkdir(f"data/Day_{i}")

for i in range(100):
    os.rename(f"data/Day_{i}",f"data/Month_{i}")