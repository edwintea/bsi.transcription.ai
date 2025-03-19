import os
import subprocess

def is_python_file(filename):
    return filename.endswith('.py')

def main():
    project_dir = r'C:\task\projects\kotoba\mom_ai'
    # List all files and directories in the project directory
    for root, dirs, files in os.walk(project_dir):
        # Filter out non-Python files
        python_files = [f for f in files if is_python_file(f)]
        if not python_files:
            # If there are no Python files in this directory, ignore it
            continue
        # Run pipreqs on the directory containing Python files
        subprocess.run(['pipreqs', root])

if __name__ == '__main__':
    main()