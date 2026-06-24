import os
import subprocess

# Paths to delete
paths_to_delete = [
    r"d:\Coding\infra-monitoring-platform\ssh_keys\devops-ubuntu_key.pem",
    r"d:\Coding\infra-monitoring-platform\generate_keys.py"
]

for path in paths_to_delete:
    if os.path.exists(path):
        try:
            os.remove(path)
            print(f"Deleted: {path}")
        except Exception as e:
            print(f"Failed to delete {path}: {e}")

# Run git commands to untrack the old key if it was tracked
try:
    print("Running git commands to stop tracking key files...")
    # Untrack the old key
    subprocess.run(["git", "rm", "--cached", "ssh_keys/devops-ubuntu_key.pem"], capture_output=True, text=True)
    # Untrack the new key (if it was somehow tracked)
    subprocess.run(["git", "rm", "--cached", "ssh_keys/infratech_key.pem"], capture_output=True, text=True)
    print("Git cache updated successfully (untracked key files).")
except Exception as e:
    print(f"Failed to run git command: {e}")
