from time import sleep
print("Please wait while I execute my tasks  ", end='', flush=True)

for x in range(3):
    for anim in r'-\|/-\|/':
        print("\b", anim, sep='', end='', flush=True)
        sleep(0.2)
print("\b")
