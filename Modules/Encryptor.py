import os
from cryptography.fernet import Fernet
import sys
import hashlib
from eth_account import Account
import json
from loguru import logger
import getpass

import wmi
c = wmi.WMI()


logical_disks = {}
for drive in c.Win32_DiskDrive():
    for partition in drive.associators("Win32_DiskDriveToDiskPartition"):
        for disk in partition.associators("Win32_LogicalDiskToPartition"):
            logical_disks[disk.Caption] = {"model":drive.Model, "serial":drive.SerialNumber}
        


def encrypt(method: str, settings_path: str):
    
    while True:
        try:
            with open(settings_path + 'to_encrypted_secrets.txt', encoding='utf-8') as file:
                data = file.readlines()
                logger.info(f'Found {len(data)} lines of keys')
                break
        except Exception as error:
            logger.error(f"Failed to open {settings_path + 'to_encrypted_secrets.txt'} | {error}")
            input("Create file and try again. Press any key to try again: ")

    json_wallets = {}
    for k in data:
        try:
            address = Account.from_key(k.replace("\n", "")).address
            json_wallets.update({
            address.lower(): k.replace("\n", "")
            })
        except Exception as error:
            logger.error(f'Cant add line: {k}')
    
    with open(settings_path + "data.txt", 'w') as file:
        json.dump(json_wallets, file)
    
    if method == 'flash':
        while True:
            answer = input(
                "Write here disk name, like: 'D'\n" + \
                ''.join(f"Disk name: {i.replace(':', '')} - {logical_disks[i]}\n" for i in logical_disks.keys())
            )
            agree = input(
                f"OK, your disk with name: {answer} | Data: {logical_disks[answer + ':']}\n" + \
                "Are you agree to encode data.txt using this data? [Y/N]: "
            )
            if agree.upper().replace(" ", "") == "Y":
                break

        data = logical_disks[answer + ":"]
        data_to_encoded = data["model"] + '_' + data["serial"]
        key = hashlib.sha256(data_to_encoded.encode()).hexdigest()[:43] + "="

    elif method == 'password':
        while True:
            data_to_be_encoded = getpass.getpass('Write here password to encrypt secret keys: ')
            agree = input(
                f"OK, Are you sure that password is correct?: {data_to_be_encoded[:4]}***\n" + \
                "Are you agree to encode data.txt using this data? [Y/N]: "
            )  
            if agree.upper().replace(" ", "") == "Y":
                break

        key = hashlib.sha256(data_to_be_encoded.encode()).hexdigest()[:43] + "="

    f = Fernet(key)
    with open(settings_path + "data.txt", 'rb') as file:
        data_file = file.read()

    encrypted = f.encrypt(data_file)

    with open(settings_path + "encoded_secrets.txt", 'wb') as file:
        file.write(encrypted)
    
    os.remove(settings_path + "data.txt")
    open(settings_path + "to_encrypted_secrets.txt", 'w')
    logger.success(f'All is ok! Check to_run_addresses.txt and run soft again')
    input("Press any key to exit")
    sys.exit()