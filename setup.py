import os
from platform import system as platform

# Print headers
INFO_HEAD = "[I] "
IMPT_HEAD = "[#] "
MISC_HEAD = "[*] "
EROR_HEAD = "[!] "

def setup_env() -> bool:
    venv_path = "venv/bin/activate"
    if platform().lower() == "windows":
        venv_path = "venv\\bin\\activate"
    if not os.path.exists(venv_path):
        print(f"{EROR_HEAD}Virtual Enviroment named \'venv\' not found, creating...")
        os.system("python3 -m venv venv")
        print(f"{INFO_HEAD}Command to enter the Virtual Enviroment (venv):\n{MISC_HEAD}Linux & Mac;source venv/bin/activate")
        print(f"{MISC_HEAD}Windows; venv\\Scripts\\activate.bat")
    try:
        import cryptography
    except ImportError:
        print(f"{EROR_HEAD}Failed to import package \'cryptography\', please import once inside of the created Virtual Enviroment.")
        print(f"{INFO_HEAD}Command to install package: \"pip install cryptography\"")
        exit(0)