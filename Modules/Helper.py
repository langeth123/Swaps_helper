
import requests
from time import sleep
from loguru import logger


LINKS = {
    "arbitrum"  : "https://arbitrum.api.0x.org/",
    "avalanche" : "https://avalanche.api.0x.org/",
    "polygon"   : "https://polygon.api.0x.org/",
    "bsc"       : "https://bsc.api.0x.org/",
    "fantom"    : "https://fantom.api.0x.org/",
    "optimism"  : "https://optimism.api.0x.org/"
}


class DexInfo:
    def __init__(self, key: str) -> None:
        self.headers = {
            "0x-api-key" : key
        }
        self.session = requests.Session()

    def send_request(self, method: str, url: str, **kwargs) -> dict or None:
        for _ in range(3):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    **kwargs
                )
                status = response.status_code

                if status == 200:
                    return response.json()
                else:
                    if status == 400 and "1inch" in url:
                        return response.json()
                    
                    logger.error(f'[0x] Bad status code: {status}')
                    sleep(5)

            except Exception as error:
                logger.error(f'[0x] Failed to do req for: {url} | {error}')
                sleep(5)
    
    def get_swap_data(self, address: str, token_in: str, token_out: str, amount: int, net_name: str) -> dict:
        kwargs = {
            "headers" : self.headers,
            "params"  : {
                "buyToken"   : token_out,
                "sellToken"  : token_in,
                "sellAmount" : str(round(amount))
            }
        }
        
        try:
            url = LINKS[net_name]
        except KeyError:
            logger.error(f'[0x] Bad net_name. Supported nets: [ {"".join(f"{i} " for i in LINKS.keys())}]')
            return

        return self.send_request("get", url + "swap/v1/quote", **kwargs)