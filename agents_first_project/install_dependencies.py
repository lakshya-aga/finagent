import subprocess
import sys

def install_packages():
    packages = ["alpha-vantage", "pandas", "python-dotenv", "scikit-learn", "hmmlearn"]
    try:
        subprocess.check_call(["uv", "pip", "install"] + packages)
        print(f"Successfully installed all packages")
    except subprocess.CalledProcessError as e:
        print(f"Error installing packages: {e}")
        sys.exit(1)

if __name__ == "__main__":
    install_packages()
