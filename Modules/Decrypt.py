import wmi, hashlib, getpass, json, cryptography
import uuid, re
from loguru import logger
from cryptography.fernet import Fernet

c = wmi.WMI()

def get_disks():
    c = wmi.WMI()
    logical_disks = {}
    for drive in c.Win32_DiskDrive():
        for partition in drive.associators("Win32_DiskDriveToDiskPartition"):
            for disk in partition.associators("Win32_LogicalDiskToPartition"):
                logical_disks[disk.Caption] = {"model":drive.Model, "serial":drive.SerialNumber}
    return logical_disks


def decrypt_files(decrypt_type: str, disk: str, settings_path: str):
    logger.info("Decrypting your secret keys..")
    logical_disks = get_disks()

    if decrypt_type == "Flash":
        disk_data = logical_disks[disk]
        data_to_be_encoded = disk_data["model"] + '_' + disk_data["serial"]
    
    elif decrypt_type == "Password":
        data_to_be_encoded = getpass.getpass('[DECRYPTOR] Write here password to decrypt secret keys: ')

    key = hashlib.sha256(data_to_be_encoded.encode()).hexdigest()[:43] + "="
    f = Fernet(key)
    while True:
        try:
            path = settings_path + 'encoded_secrets.txt'
            with open(path, 'rb') as file:
                file_data = file.read()
                break
        except Exception as error:
            logger.error(f'Error with trying to open file encoded_secrets.txt! {error}')
            input("Fix it and press enter: ")
    try:

        return json.loads(f.decrypt(file_data).decode())
    except cryptography.fernet.InvalidToken:
        logger.error("Key to Decrypt files is incorrect!")
        return decrypt_files(decrypt_type, disk, settings_path)