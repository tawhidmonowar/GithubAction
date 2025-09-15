import sys
import subprocess

def run_script(script_path):

    print(f"--- Running {script_path} ---")
    try:
        subprocess.run([sys.executable, script_path], check=True, cwd='./data_processing')
        print(f"--- {script_path} ran successfully ---")
        return True
    except subprocess.CalledProcessError as e:
        print(f"--- Error: {script_path} failed with exit code {e.returncode} ---")
        return False
    except FileNotFoundError:
        print(f"--- Error: {script_path} not found ---")
        return False


def main():
    print("Starting data processing workflow...")

    scripts_to_run = [
        'split_hashtags.py',
        'update_chunks.py',
        'merge_hashtags.py'
    ]

    for script in scripts_to_run:
        if not run_script(script):
            print(f"--- Workflow aborted due to failure in {script} ---")
            sys.exit(1)

    print("All data processing scripts completed successfully.")

if __name__ == "__main__":
    main()