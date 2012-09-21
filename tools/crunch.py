import subprocess
for i in range(0, 100):
    subprocess.call(["../main.py", str(i)])