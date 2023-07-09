from os import getcwd

autosoft = """

 _______          _________ _______  _______  _______  _______ _________
(  ___  )|\     /|\__   __/(  ___  )(  ____ \(  ___  )(  ____ \\__   __/
| (   ) || |   | |   ) (   | (   ) || (    \/| (   ) || (    \/   | |   
| (___) || |   | |   | |   | |   | || (_____ | |   | || (__       | |   
|  ___  || |   | |   | |   | |   | |(_____  )| |   | ||  __)      | |   
| (   ) || |   | |   | |   | |   | |      ) || |   | || (         | |   
| )   ( || (___) |   | |   | (___) |/\____) || (___) || )         | |   
|/     \||_______|   |_|   (_______)\_______)(_______)|/          |_|   

"""
subs_text = """
You have purchased an AutoSoft software license.
Thank you for your trust.
Link to the channel with announcements: t.me/swiper_tools
Ask all questions in our chat.

"""

print(autosoft)
print(subs_text)


from config import *
from Modules.Account import Account
from Modules.TaskHandler import TaskHandler
from threading import Thread
threads = []


def main(secret):
    acc_ = Account(secret)
    task = Thread(target=TaskHandler(acc_).start_handler)
    threads.append(task)
    task.start()

    time_range = SETTINGS["ThreadRunnerSleep"]
    timing = random.randint(time_range[0], time_range[1])
    logger.info(f'[Thread Runner] Sleeping for: {timing} s')
    sleep(timing)
