#!/usr/bin/python
import subprocess
import sys
# ================================================================
# = Automated runs of the EBM Scheduler with variable conditions =
# ================================================================

if __name__ == "__main__":
    """Handle command line args."""
    algorithm = sys.argv[1] if len(sys.argv)>1 else 0
    lax = 6 if algorithm > 0 else 2

    for i in range(0, 10):
        """Load initial condition dataset corresponding to i."""
        for weight in range(0, 11):
            """Vary weight from 0 to 1.0. Increment by 0.1."""
            for relax in range(1, lax):
                """Vary the relaxing ten to fifty percent."""
                subprocess.call(["../main.py", str(algorithm), str(i), str(weight), str(relax)])