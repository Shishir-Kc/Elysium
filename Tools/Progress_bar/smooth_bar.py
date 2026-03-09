import os ,sys
import time

def smooth_progress(duration=3, bar_length=50,text='Restarting'):
    blocks = " ▏▎▍▌▋▊▉█"
    steps = 100

    for i in range(steps + 1):
        progress = i / steps
        full = int(progress * bar_length)
        remainder = (progress * bar_length) - full
        partial = int(remainder * (len(blocks) - 1))

        bar = "█" * full
        if full < bar_length:
            bar += blocks[partial]
            bar += " " * (bar_length - full - 1)

        sys.stdout.write(f"\r{text} [{bar}] {progress*100:5.1f}%")
        sys.stdout.flush()
        

        time.sleep(duration / steps)
    sys.stdout.write("\r" + " " * 80 + "\r")
    
    sys.stdout.flush()

    print()
