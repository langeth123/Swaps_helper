try:
    from config import *

except SystemExit:
    pass

except:
    import traceback
    from sys import exit
    print(traceback.format_exc())
    input("\nPress any key to exit")
    exit()



if __name__ == "__main__":
    try:
        from run import *
        random.shuffle(runner_secrets)
    
        for i in runner_secrets:
            main(i)
            
        for i in threads:
            i.join() 

    except Exception as error:
        if 'json' in str(traceback.format_exc()):
            print(f'Check your settings.json file, here is bad data')
        else:
            print(traceback.format_exc())
            print(f'Fatal error occured to soft: {error}')

    print(f'Soft successfully end work. Check results here --> https://clck.ru/3vyXS <--')
    input("Press any key to exit")
