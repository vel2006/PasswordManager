# PasswordManager

### Current Version
1.0

## Requirements

1) Python3 is a requrirement for this script, as it uses the "match" statement.

2) Python Cryptography Package, this is due to the hashing and encryption algorithms used are within this package. It is suggested to use version 48.0.0 or newer as that is what the script has been tested and written in.

## Usage

When the script first starts it will check for a python virtual eniroment named 'venv', in the event that it is not named, the script will create it along with providing the needed commands to enter the virtual enviroment.

Once the script starts and all imports are handled, first the script will check for the file "password.enc", this is where every password and platform is held, if the file does not exist you will be prompted with the setup configuration for it. If for whatever reason the file is empty (bad write or other write based bug) the file will be deleted, you will have to run the script again using the backup file if not deleted.

When the "password.enc" file exists and contains data the script will attempt to decrypt the data using the passed password from the user.

## Security and Reliability

While this script does not provide any type of integrity check or restrict access to the data it does provide a secure method of encryption and reliable method of storing the user's data.

The script will encrypt all data within the "password.enc" file with ChaCha20, the key and nonce values are based off of the passed password. When the user enters a password it is hashed using SHA2-512, the first 32 bytes are used as the decryption key and the last 16 bytes are used as the nonce value for ChaCha20.

As to ensure that there is minimal dataloss in the event of a failed write, or some other issue when the data from "password.enc" is read a copy named "password.back.enc" is written. Along with that data is only overwritten when the user uses the "end" command within the main user loop.

In the event you will need to use the backup, simply removing the "password.enc" file and renaming "password.old.enc" to "password.enc" will allow you to use the backup file.

## Security Warnings

While the current design is vulnerable to four main types of attacks, those being; "Two-Time pad", "RAM Scrapping", Non Protected Path and Low Entropy attacks. The reasoning for these are explained below;

Low Entropy: Due to the master password / encryption key being based on a user's chosed password with no requirements it is possible that someone could set the password as a combination of words which would be quite easy to bruteforce against random letters, number and symbols.

Two-Time pad: Due to the same nonce being used on every time encryption is used.

RAM Scraping: Due to the passwords being held in cleartext once loaded from the file and decrypted, malware which a high enough permissions could in theory read the cleartext passwords and the associated platform.

Non Protected Path: Due to the script holding the passwords file in the same directory as is within, that means that if placed in a directory like "C:\Users\Public" for example anyone could access the password file and attempt to decrypt the data. Another attack could be someone deleting the "password.enc" and "password.old.enc" files. This also means that if several users use the exact same script and "password.enc" file, then any user could see every other user's passwords.

All of these are planned to be fixed in version 1.1. This first version is only to establish a baseline which will be used to work off of and a potential fallback if future methods of key and nonce generation are not reliable or secure.