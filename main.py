import os
from time import sleep
from setup import setup_env
from getpass import getpass
from ast import literal_eval
from platform import system as os_platform
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# Print headers
INFO_HEAD = "[I] "
IMPT_HEAD = "[#] "
MISC_HEAD = "[*] "
EROR_HEAD = "[!] "

# Decrypting data
def decrypt_data(data: bytes, key: bytes, nonce: bytes) -> bytes:
    algorithm = algorithms.ChaCha20(key, nonce)
    cipher = Cipher(algorithm, mode=None)
    decryptor = cipher.decryptor()
    output_data = decryptor.update(data)
    return output_data

# Encrypting data
def encrypt_data(data: bytes, key: bytes, nonce: bytes) -> bytes:
    algorithm = algorithms.ChaCha20(key, nonce)
    cipher = Cipher(algorithm, mode=None)
    encryptor = cipher.encryptor()
    output_data = encryptor.update(data)
    return output_data

# Reading a passed file
def read_file(file_path: str) -> bytes|None:
    file_data = None
    try:
        with open(file_path, "rb") as file_handle:
            file_data = file_handle.read()
            file_handle.close()
    except FileNotFoundError:
        print(f"{EROR_HEAD}OOPS, That file does not exist :(")
    except PermissionError:
        print(f"{EROR_HEAD}OOPS, You can\'t access that file :)")
    return file_data

# Writing to a file
def write_to_file(file_path: str, data: bytes) -> bool:
    state = False
    try:
        with open(file_path, "wb") as file_handle:
            file_handle.write(data)
            file_handle.close()
        state = True
    except PermissionError:
        print(f"{EROR_HEAD}OOPS, You can\'t access that file :)")
    return state

# Adding site data to the known ones
def add_site_data(password_data: dict) -> dict:
    global hash_attempt
    print(f"{MISC_HEAD}Please input the platform you wish to save the password for.")
    platform = input(">").rstrip("\n")
    print(f"{MISC_HEAD}Please input the password for that platform.")
    password = getpass(">").rstrip("\n")
    if platform in password_data.keys():
        if password in password_data[platform]:
            print(f"{EROR_HEAD}Password \"{password}\" is already within this platform, not adding.")
        else:
            password_data[platform].append(password)
    else:
        password_data[platform] = [password]
    byte_data = bytes(f"{password_data}", "utf-8")
    encrypted_data = encrypt_data(byte_data, hash_attempt[:32], hash_attempt[-16:])
    write_to_file("password.enc", encrypted_data)
    return password_data

# Removing site data from the known ones
def rem_site_data(password_data: dict) -> dict:
    print(f"{MISC_HEAD}Please input the platform you wish to remove the password for.")
    platform = input(">").rstrip("\n")
    if platform not in password_data.keys():
        print(f"{EROR_HEAD}Site \"{platform}\" is not within the saved platforms.")
        return password_data
    print(f"{MISC_HEAD}Please input the password for that platform.")
    password = getpass(">").rstrip("\n")
    if password not in password_data[platform]:
        print(f"{EROR_HEAD}Password \"{password}\" is not within the saved passwords.")
        return password_data
    password_data[platform].remove(password)
    if len(password_data[platform]) == 0:
        password_data.pop(platform)
    byte_data = bytes(f"{password_data}", "utf-8")
    encrypted_data = encrypt_data(byte_data, hash_attempt[:32], hash_attempt[-16:])
    write_to_file("password.enc", encrypted_data)
    return password_data

# Deleting a site's data from the known ones
def del_site_data(password_data: dict) -> dict:
    print(f"{MISC_HEAD}Please input the platform you wish to remove the password for.")
    platform = input(">").rstrip("\n")
    if platform not in password_data.keys():
        print(f"{EROR_HEAD}Site \"{platform}\" is not within the saved platforms.")
        return password_data
    password_data.pop(platform)
    byte_data = bytes(f"{password_data}", "utf-8")
    encrypted_data = encrypt_data(byte_data, hash_attempt[:32], hash_attempt[-16:])
    write_to_file("password.enc", encrypted_data)
    return password_data

# Hashing a password
def hash_password(password: bytes) -> bytes:
    digest = hashes.Hash(hashes.SHA512())
    digest.update(password)
    hash_attempt = digest.finalize()
    return hash_attempt

def clear_screen():
    system_os = os_platform().lower()
    if system_os == "windows":
        os.system("cls")
    else:
        os.system("clear")

if __name__ == "__main__":
    setup_env()

    attempt = 0
    file_data = None
    if os.path.exists("password.enc"):
        file_data = read_file("password.enc")
        if len(file_data) == 0:
            print(f"{INFO_HEAD}File is corrupted, no data is saved, deleting...")
            os.remove("password.enc")
            exit(0)
    else:
        # Setting up the password.enc file
        print(f"{INFO_HEAD}password.enc was not found, assuming first timr running script...")
        password_data = add_site_data({})
        print(f"{INFO_HEAD}Please input the master password, this will be used to decrypt the stored passwords, I would suggest writing this down.")
        hash_attempt = None
        while True:
            password = input(">").rstrip("\n")
            password_bytes = None
            try:
                password_bytes = bytes(password, "utf-8")
            except Exception:
                print(f"{EROR_HEAD}OOPS, That input was not valid UTF-8!")
            if password_bytes is not None:
                if hash_attempt is None:
                    hash_attempt = hash_password(password_bytes)
                else:
                    attempt_two = hash_password(password_bytes)
                    if hash_attempt == attempt_two:
                        print(f"{INFO_HEAD}That password will work, encrypting saved password...")
                        break
                    else:
                        print(f"{EROR_HEAD}Those passwords do not match, please try again.")
                        hash_attempt = None
        data_bytes = bytes(f"{password_data}", "utf-8")
        data_enc = encrypt_data(data_bytes, hash_attempt[:32], hash_attempt[-16:])

        # Checking the reading, writing and input functionality on the current device
        print(f"{MISC_HEAD}Password encrypted, checking file integrity...")
        write_to_file("password.enc", data_enc)
        file_data = read_file("password.enc")
        if file_data != data_enc:
            print(f"{EROR_HEAD}Aborting script, passwords cannot be read!")
            exit(0)
        data_decrypt = decrypt_data(file_data, hash_attempt[:32], hash_attempt[-16:])
        if data_decrypt != data_bytes:
            print(f"{EROR_HEAD}Aborting script, passwords cannot be decrypted!")
            exit(0)
        while True:
            print(f"{MISC_HEAD}Please type the decryption password.")
            password_attempt = input(">")
            bytes_attempt = None
            try:
                bytes_attempt = bytes(password_attempt, "utf-8")
            except Exception:
                print(f"{EROR_HEAD}Please input a UTF-8 valid attempt.")
        decrypted_bytes = None
        if bytes_attempt is not None:
            hash_attempt = hash_password(bytes_attempt)
            decrypted_bytes = decrypt_data(file_data, hash_attempt[:32], hash_attempt[-16:])
            if decrypted_bytes != data_bytes:
                print(f"{EROR_HEAD}Aborting script, input password cannot be converted into key!")
        try:
            decoded_bytes = decrypted_bytes.decode("utf-8")
            decoded_bytes = literal_eval(decoded_bytes)
        except Exception as error:
            print(f"{EROR_HEAD}Encountered error when decoding data: {error}")
            exit(0)
        if decoded_bytes != password_data:
            print(f"{EROR_HEAD}Aborting script, failed to decrypt data with input password!")
            exit(0)
        print(f"{INFO_HEAD}password.enc file setup and tested!")

    # Main password input loop
    while attempt < 3:
        write_to_file("password.old.enc", file_data)
        print(f"{MISC_HEAD}Please input the decryption password.")
        password_attempt = getpass(">").rstrip("\n")
        bytes_attempt = None
        try:
            bytes_attempt = bytes(password_attempt, "utf-8")
        except Exception:
            print(f"{EROR_HEAD}Please input a UTF-8 valid attempt.")
        if bytes_attempt is not None:
            hash_attempt = hash_password(bytes_attempt)
            decrypted_bytes = decrypt_data(file_data, hash_attempt[:32], hash_attempt[-16:])
            decrypted_data = None
            try:
                decrypted_data = decrypted_bytes.decode("utf-8")
                decrypted_data = literal_eval(decrypted_data)
            except Exception:
                print(f"{EROR_HEAD}OOPS, Failed to decode that password data, guess you failed, are you new to this? >:P")
                decrypted_data = None
                attempt += 1
            if decrypted_data is not None:
                print(f"{INFO_HEAD}Decrypted passwords.")
                attempt = 5
                break
    if attempt != 5:
        print(f"{INFO_HEAD}What was that password again? KEK!")
        exit(0)

    # User input loop
    while True:
        clear_screen()
        print(f"{INFO_HEAD}Select one of the following;\n{MISC_HEAD}add | Adds a password to the requested platform.")
        print(f"{MISC_HEAD}rem | Removes a password for the requested platform.\n{MISC_HEAD}del | Delete all passwords for the requested platform.")
        print(f"{MISC_HEAD}sho | Shows passwords for requested platform.\n{MISC_HEAD}all | Shows passwords for all platforms.")
        print(f"{MISC_HEAD}plt | Shows platforms and their saved password count.\n{MISC_HEAD}end | End this session and save the passwords.")
        choice = input(">").lower().rstrip("\n")
        match choice:
            case "add":
                decrypted_data = add_site_data(decrypted_data)
            case "rem":
                decrypted_data = rem_site_data(decrypted_data)
            case "del":
                decrypted_data = del_site_data(decrypted_data)
            case "plt":
                for platform in decrypted_data.keys():
                    print(f"{MISC_HEAD}Held {platform}: {len(decrypted_data[platform])}")
            case "sho":
                print(f"{MISC_HEAD}Please input the platform that you wish to display the passwords of.")
                platform = input(">")
                if platform in decrypted_data.keys():
                    for password in decrypted_data[platform]:
                        print(f"{MISC_HEAD}{platform}: {password}")
                else:
                    print(f"{EROR_HEAD}The platform \"{platform}\" is not a known platform.")
            case "all":
                for platform in decrypted_data.keys():
                    for password in decrypted_data[platform]:
                        print(f"{MISC_HEAD}{platform}: {password}")
            case "end":
                break
        print(f"{MISC_HEAD}Press <Enter> to continue...")
        input(">")
    bytes_data = bytes(f"{decrypted_data}", "utf-8")
    encrypted_data = encrypt_data(bytes_data, hash_attempt[:32], hash_attempt[-16:])
    write_to_file("password.enc", encrypted_data)