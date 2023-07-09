from config import *
from Modules.Account import Account
from threading import Thread
from Modules.Swaps import swap_handler

class TaskHandler:
    def __init__(self, account: Account) -> None:
        self.account = account
        self.address = account.address


    def start_handler(self):
        task_number = SETTINGS["TaskNumber"]

        if task_number == 1:
            swap_handler(self.account)
        