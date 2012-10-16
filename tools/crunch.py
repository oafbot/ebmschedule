import subprocess
for weight in range(0, 11):
    for relax in range(1, 6):  
        subprocess.call(["../main.py", str(0), str(weight), str(relax)])