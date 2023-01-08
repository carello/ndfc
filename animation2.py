from time import sleep

def animation_hash(percent=0, width=30):
    hashes = width * percent // 100
    blanks = width - hashes

    print("\r[", hashes*"#", blanks*" ", "]", f"{percent:.0f}%", sep="", end="", flush=True)

print("Please wait while I run my tasks")
for i in range(101):
    animation_hash(i)
    sleep(0.1)

print()
