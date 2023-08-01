from config import *
from Modules.Helper import DexInfo
from Modules.Account import Account, get_w3
from Modules.Parser import checker
from Modules.Inch import get_data_for_inch

def get_availible_tokens(account: Account, first=False):
    all_balances = asyncio.run(checker(account.address))
    time.sleep(1)
    availible_tokens = []
    parsed_res = f"========= {account.address} ===========\n\n"

    for i in all_balances["native"]:
        parsed_res += f'{i["net_name"].ljust(10)} - {str(round(Web3.from_wei(i["balance"], "ether"), 5)).ljust(9)} {NATIVE[i["net_name"]]}\n'

    parsed_res += "\n"

    for j in all_balances["tokens"]:
        if j["balance"] / 10**j["decimal"] > 0.00005:
            availible_tokens.append(j)
        parsed_res += f'{j["net_name"].ljust(10)} - {j["token_name"].ljust(5)} - {round(j["balance"] / 10**j["decimal"], 4)}\n'
    
    parsed_res += "\n================================================================"
    
    if first:
        print(parsed_res)

    return availible_tokens

def get_swap_data(account: Account, *args):
    while True:
        inch_data = get_data_for_inch(*args)
        if inch_data == "allowance":
            account.approve_token(args[1], args[4], Web3.to_checksum_address("0x1111111254eeb25477b68fb85ed929f73a960582"))
        else:
            if inch_data is None:
                logger.error(f'[{args[0]}] Failed to get response from 1inch')
                break
            else:
                if "tx" in inch_data.keys():
                    logger.success(f'[{args[0]}] Got info from 1inch')
                    return {
                        "to": "0x1111111254eeb25477b68fb85ed929f73a960582",
                        "data": inch_data["tx"].get("data")
                    }
            
    dex_helper = DexInfo(SETTINGS["0xKey"])
    data = dex_helper.get_swap_data(*args)

    return data
                
    
    


def swap_handler(account: Account):
    for i in range(get_random_number("SwapsAmount")):
        while True:
            try:
                if i == 0:
                    availible_tokens = get_availible_tokens(account, first=True)
                else:
                    availible_tokens = get_availible_tokens(account)

                if len(availible_tokens) == 0:
                    account.info(f'Zero availible tokens')
                    return

                random_token_in = random.choice(availible_tokens)
                net_name = random_token_in["net_name"]
                token_address = random_token_in["token_address"]

                random_token_out = random.choice([Web3.to_checksum_address(i) for i in SETTINGS["TOKENS"][net_name].values() if i.lower() != token_address.lower()])
                to_swap_amount = random_token_in["balance"]
            
                data = get_swap_data(account, account.address, token_address, random_token_out, to_swap_amount, net_name)
            
                account.approve_token(token_address, net_name, Web3.to_checksum_address(data["to"]))

                tx = account.get_tx_data(get_w3(net_name), net_name)
                tx["data"] = data["data"]
                tx["to"] = Web3.to_checksum_address(data["to"])

                hash = account.send_transaction(tx, net_name)
                if account.wait_until_tx_finished(hash, net_name):
                    sleeping(account.address)
                    break

            except Exception as error:
                if 'gas' in str(error).lower():
                    break
                else:
                    account.error(f'Handler: {error}')
                    sleeping(account.address)
    
    if SETTINGS["SwapInEnd"] is True:
        availible_tokens = get_availible_tokens(account, first=True)

        if len(availible_tokens) == 0:
            account.info(f'Zero availible tokens')
            return
        
        random.shuffle(availible_tokens)

        for random_token_in in availible_tokens:
            try:
                net_name = random_token_in["net_name"]
                token_address = random_token_in["token_address"]

                if token_address not in STARGATE[net_name]:

                    if net_name in STARGATE.keys():
                        random_token_out = random.choice(STARGATE[net_name])

                        to_swap_amount = random_token_in["balance"]
                    
                        data = get_swap_data(account, account.address, token_address, random_token_out, to_swap_amount, net_name)
                    
                        account.approve_token(token_address, net_name, Web3.to_checksum_address(data["to"]))

                        tx = account.get_tx_data(get_w3(net_name), net_name)
                        tx["data"] = data["data"]
                        tx["to"] = Web3.to_checksum_address(data["to"])

                        hash = account.send_transaction(tx, net_name)
                        if account.wait_until_tx_finished(hash, net_name):
                            sleeping(account.address)

            except Exception as error:
                if 'gas' in str(error).lower():
                    continue
                else:
                    account.error(f'End Handler: {error}')
                    sleeping(account.address)
