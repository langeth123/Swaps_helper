from config import *
import subprocess
import uuid, re
import hashlib
import socket
from Modules.KEY import USER_KEY

KEY = "CEy426oSSaOTWDPgtuKxm1nS2uWN_4-L_eyt0dmAr40="


def decrypt(filename):
    f = Fernet(KEY)
    with open(filename, 'rb') as file:
        encrypted_data = file.read()
    decrypted_data = f.decrypt(encrypted_data).decode()
    return decrypted_data.split(':')


server_data = decrypt(f"{SETTINGS_PATH}server_data.txt")
connect_data = (server_data[0], int(server_data[1]))

def check_license_elig(sha):
    logger.info("Checking license expiration date...")
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(connect_data)
        message = {
            "auth": 'swaps',
            "key": sha
        }
        client.send(json.dumps(message).encode())
        response = client.recv(1024).decode()
        client.close()
        if response == "True":
            return True
        else:
            logger.error(f'Cant auth your device/subs')
            input("Press any key to exit")
            exit()
    except Exception as error:
        logger.error(f'SEnd this message to dev: {error}')
        input("Press any key to exit")
        exit()


def checking_license():
    text = wmi.WMI().Win32_ComputerSystemProduct()[0].UUID + ':SOFT'
    sha = hashlib.sha1(text.encode()).hexdigest()
    if sha != USER_KEY:
        logger.error(f'Cant validate your pc. Write to dev')
        input("Press any key to exit")
        exit()
    else:
        return check_license_elig(sha)