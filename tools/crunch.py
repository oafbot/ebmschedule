import subprocess
# ================================================================
# = Automated runs of the EBM Scheduler with variable conditions =
# ================================================================

for i in range(0, 10):
    """Load initial condition dataset corresponding to i."""
    for weight in range(0, 11):
        """Vary weight from 0 to 1.0. Increment by 0.1."""
        for relax in range(1, 6):
            """Vary the relaxing ten to fifty percent."""
            subprocess.call(["../main.py", str(i), str(weight), str(relax)])