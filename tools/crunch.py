import subprocess
for i in range(0, 10):
    subprocess.call(["../main.py", str(i)])