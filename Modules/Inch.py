import requests
from Modules.Helper import DexInfo
import time

INCH_URL = "https://api-defillama.1inch.io"
INCH_VER = 5

CHAINS_ID = {
    'avalanche' : 43114,
    'polygon'   : 137,
    'ethereum'  : 1,
    'bsc'       : 56,
    'arbitrum'  : 42161,
    'optimism'  : 10,
    'fantom'    : 250
}

headers = {
    'authority': 'api-defillama.1inch.io',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,uk;q=0.6,pl;q=0.5,cy;q=0.4,fr;q=0.3',
    'cache-control': 'max-age=0',
    'if-none-match': 'W/"881-sjxAEIcDeTIyvhdXc7Xp3XMcK+s"',
    'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
}

def get_data_for_inch(
        address: str, token_in:str, 
        token_out: str, amount: int,
        net_name: str
):

    if token_in == "ETH":
        token_in = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
    elif token_out == "ETH":
        token_out = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"

    url = f'{INCH_URL}/v{INCH_VER}.0/{CHAINS_ID[net_name]}/swap?fromTokenAddress={token_in}&toTokenAddress={token_out}&amount={amount}&fromAddress={address}&slippage=2'
    response = DexInfo("").send_request("get", url, headers=headers)

    if type(response) is dict:
        if "tx" in response.keys():
            return response
        else:
            if "Not enough allowance" in str(response):
                return "allowance"