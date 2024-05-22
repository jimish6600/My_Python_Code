name = {
    "jimish" : "patel",
    "rahil" : "mansuri"
}

print(name["jimish"])
print(name.get("jimi"))

name.update({"vishal":"sharm"})

# name.clear()
name.pop("jimish")
for key,item in name.items():
    print(f"{key} : {item}")

