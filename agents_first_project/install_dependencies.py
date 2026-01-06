import subprocess
import sys

def install_packages():
    packages = ["alpha_vantage", "pandas", "python-dotenv", "scikit-learn", "hmmlearn"]
    for package in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"Successfully installed {package}")
        except subprocess.CalledProcessError as e:
            print(f"Error installing {package}: {e}")
            sys.exit(1)

if __name__ == "__main__":
    install_packages()
