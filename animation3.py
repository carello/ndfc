
import time

def animation_dot():
    print("Please wait while I run my tasks", end="")
    for i in range(10):
        time.sleep(1)
        print('.', end="", flush=True)
    print()


animation_dot()
