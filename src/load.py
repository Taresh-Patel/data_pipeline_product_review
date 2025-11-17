import os
import subprocess
import shutil

def load_data():
    file_path = "data/processed/"
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Processed file not found: {file_path}")

    # Detect Git executable dynamically
    git_cmd = shutil.which("git")
    if not git_cmd:
        git_cmd = r"C:\Users\TOS37804-T.Patel\AppData\Local\Programs\Git\bin\git.exe"  # Fallback path
        if not os.path.exists(git_cmd):
            raise EnvironmentError("Git executable not found. Please install Git or update fallback path.")

    # Initialize repo if missing
    if not os.path.exists(".git"):
        subprocess.run([git_cmd, "init"], check=True)
        subprocess.run([git_cmd, "branch", "-M", "main"], check=True)
        subprocess.run([git_cmd, "remote", "add", "origin",
                        "https://github.com/Taresh-Patel/data_pipeline_product_review.git"], check=True)

    # Stage the processed file
    subprocess.run([git_cmd, "add", file_path], check=True)

    # Configure Git user details
    subprocess.run([git_cmd, "config", "user.name", "Taresh-Patel"], check=True)
    subprocess.run([git_cmd, "config", "user.email", "Taresh_Patel@outlook.com"], check=True)

    # Commit even if no changes
    subprocess.run([git_cmd, "commit", "--allow-empty", "-m", "Publish processed data"], check=True)

    # Try pushing, if fails due to remote ahead, pull with local preference and retry
    try:
        subprocess.run([git_cmd, "push", "-u", "origin", "main"], check=True)
    except subprocess.CalledProcessError:
        print("Push failed. Attempting to pull with local preference and retry...")
        subprocess.run([
            git_cmd, "pull", "origin", "main",
            "--allow-unrelated-histories",
            "--strategy-option", "ours",
            "-m", "Auto merge"
        ], check=True)
        subprocess.run([git_cmd, "push", "-u", "origin", "main"], check=True)

    print(f"Published {file_path} to GitHub at https://github.com/Taresh-Patel/data_pipeline_product_review.git")

if __name__ == "__main__":
    load_data()