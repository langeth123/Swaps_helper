from config import *
from random import choice, randint

async def check_data_token(token_address: str, net_name: str):
    try:
        web3 = choice(ASYNC_RPC[net_name])
        address = Web3.to_checksum_address(token_address)

        token_contract  = web3.eth.contract(address=address, abi=ERC20_ABI)
        decimals        = await token_contract.functions.decimals().call()

        return token_contract, decimals
    
    except Exception as error:
        if 'Too Many Requests' in str(error):
            logger.error(f'{net_name} - Ratelimited! Thread sleeping 15-30 seconds')
            await asyncio.sleep(randint(15, 30))
        else:
            logger.error(f'[{token_address}] | {error} ({net_name})')
            await asyncio.sleep(2)
        return await check_data_token(token_address, net_name)

async def check_balance(way='stable', **kwargs):
    try:
        net_name, wallet = kwargs["net_name"], Web3.to_checksum_address(kwargs["wallet"])
        web3 = choice(ASYNC_RPC[net_name])

        if way == 'stable':
            address = Web3.to_checksum_address(kwargs["token_address"])
            token_contract, token_decimal = await check_data_token(kwargs["token_address"], net_name)
            balance = await token_contract.functions.balanceOf(wallet).call()
        else:
            address = ""
            token_decimal = 0
            balance = await web3.eth.get_balance(wallet)

        return {"net_name": net_name, "balance": balance, 
                'decimal': token_decimal, "token_name": kwargs["token_name"],
                "token_address": address}

    except Exception as error:
        if 'Too Many Requests' in str(error):
            logger.error(f'[{wallet}] {net_name} - Ratelimited! Thread sleeping 1-5 seconds')
            await asyncio.sleep(3)
        else:
            logger.error(f'[{wallet}] | {error}')
            await asyncio.sleep(2)
        return await check_balance(way=way, **kwargs)


async def checker(address):
    tokes_res = []
    tokens = SETTINGS.get("TOKENS")

    logger.info(f"[{address}] Start fetching tokens")

    for net_name in tokens:
        tasks = []

        for token_name in tokens[net_name]:
            data = {
                "net_name": net_name, 
                "token_address": tokens[net_name][token_name], 
                "token_name": token_name,
                "wallet": address
            }
            tasks.append(asyncio.create_task(check_balance(**data)))
        
        parse_res = await asyncio.gather(*tasks)

        for l in parse_res:
            tokes_res.append(l)

        #tokes_res.append({"net_name": net_name, 'res': parse_res})

    #logger.success(f"[{address}] All tokens was fetched! Start checking native currencies")

    tasks = [asyncio.create_task(
        check_balance(way='s', **{"wallet": address, "net_name": net_name, "token_name": "native"})
    )   for net_name in ASYNC_RPC.keys()]

    logger.success(f"[{address}] All balances was fetched")
    
    return {
        "address": address,
        "native": await asyncio.gather(*tasks),
        "tokens": tokes_res
    }