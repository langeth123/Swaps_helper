
from config import (
    CONNECTED_RPCS,
    acc,
    logger,
    sleep,
    sleeping,
    random,
    web3,
    SETTINGS,
    Web3,
    ERC20_ABI,
    time
)

def get_w3(net_name: str):
    w3 = random.choice(CONNECTED_RPCS.get(net_name))
    return w3

class Account:
    def __init__(self, secret_key: str) -> None:
        self.eth_account = acc.from_key(secret_key)
        self.address = self.eth_account.address
        self.secret_key = secret_key

    def wait_until_tx_finished(self, hash: str, net_name: str, max_time=500) -> bool:
        w3 = get_w3(net_name)
        start_time = time.time()
        while True:
            try:
                if time.time() - start_time > max_time:
                    logger.error(f'[{self.address}] [{hash}] transaction is failed (timeout)')
                    return False
                receipts = w3.eth.get_transaction_receipt(hash)
                status = receipts.get("status")

                if status == 1:
                    logger.success(f"{hash} is completed")
                    return True
                elif status is None:
                    #print(f'[{hash}] still processed')
                    sleep(0.3)
                elif status != 1:
                    logger.error(f'[{self.address}] [{hash}] transaction is failed')
                    return False
            except web3.exceptions.TransactionNotFound:
                #print(f"[{hash}] still in progress")
                sleep(1)

    def get_contract(self, token_address: str, net_name: str, token=False):
        w3 = get_w3(net_name)

        if token:
            abi = token
        else: abi = ERC20_ABI

        contract = w3.eth.contract(token_address, abi=abi)
        return contract, w3
    
    def send_transaction(self, tx: dict, net_name: str, approve=False) -> str: 
        w3 = get_w3(net_name)

        if net_name == 'zksync':
            if approve is False:
                gasEstimate = w3.eth.estimate_gas(tx) / SETTINGS["TxCoeff"]
            else:
                gasEstimate = w3.eth.estimate_gas(tx) / SETTINGS["TxCoeffApprove"]
        else: gasEstimate = w3.eth.estimate_gas(tx)

        tx['gas'] = round(gasEstimate)
        signed_txn = w3.eth.account.sign_transaction(tx, private_key=self.eth_account.key)

        tx_token = w3.to_hex(w3.eth.send_raw_transaction(signed_txn.rawTransaction))
        logger.success(f"Approved: {tx_token}")
        sleeping("Take a sleep...")

        return tx_token

    
    def get_gas_price(self, net_name: str):
        w3 = get_w3(net_name)
        max_gas = Web3.to_wei(SETTINGS.get("GWEI").get(net_name), 'gwei')

        while True:
            try:
                gas_price = w3.eth.gas_price
                if gas_price > max_gas:
                    h_gas, h_max = Web3.from_wei(gas_price, 'gwei'), Web3.from_wei(max_gas, 'gwei')
                    logger.error(f'[{self.address}] Sender net: {net_name}. Current gasPrice: {h_gas} | Max gas price: {h_max}')
                    sleeping(f'[{self.address}] Waiting best gwei. Update after ')
                else:
                    return round(gas_price)
                
            except Exception as error:
                logger.error(f'[{self.address}] Error: {error}')
                sleeping(f'[{self.address}] Error fault. Update after ')

    def get_tx_data(self, w3: Web3, net_name: str, value=0) -> dict:
        gas_price = self.get_gas_price(net_name)
        data = {
            'chainId': w3.eth.chain_id, 
            'nonce': w3.eth.get_transaction_count(self.address),  
            'from': self.address, 
            "value": value
        }
        if net_name in ["avalanche", "polygon", "arbitrum"]:
            data["type"] = "0x2"

        if net_name not in ['arbitrum', "avalanche", "polygon"]:
            data["gasPrice"] = gas_price
            
        else:
            data["maxFeePerGas"] = gas_price
            if net_name == "polygon":
                data["maxPriorityFeePerGas"] = Web3.to_wei(30, "gwei")
            elif net_name == "avalanche":
                data["maxPriorityFeePerGas"] = gas_price
            elif net_name == "ethereum":
                data["maxPriorityFeePerGas"] = Web3.to_wei(0.05, "gwei")
            elif net_name == "arbitrum":
                data["maxPriorityFeePerGas"] = Web3.to_wei(0.01, "gwei")
        return data
    
    def get_balance(self, token_address=None, net_name=None, contract=False, get_decimals=False):
        while True:
            try:
                if contract == False:
                    contract, w3 = self.get_contract(token_address, net_name)
                decimals    = contract.functions.decimals().call()
                balance     = contract.functions.balanceOf(self.address).call()

                from_wei_balance = balance / 10**decimals
                if get_decimals:

                    return balance, from_wei_balance, decimals
                
                return balance, float(from_wei_balance)
            except Exception as error:
                logger.error(f'[{self.address}] Cant get balance of: {token_address}! Error: {error}')
                sleep(5)

    def get_native_balance(self, net_name: str):
        while True:
            try:
                w3 = get_w3(net_name)
                balance = w3.eth.get_balance(self.address)

                return balance
            except Exception as error:
                logger.error(f'[{self.address}] Cant get balance of native: {net_name}! Error: {error}')
                sleeping(f'[{self.address}] Error fault. Update after ')


    def approve_token(self, token_address: str, net_name: str, spender: str, amount=False):
        def __check_allowance__():
            amount_approved = contract.functions.allowance(self.address, spender).call()

            if amount_approved < balance:
                while True:
                    try:
                        tx = contract.functions.approve(spender, balance).build_transaction(
                            self.get_tx_data(w3, net_name)
                        )
                        return tx
                    except Exception as error:

                        import traceback
                        print(traceback.format_exc())
                        logger.error(f'[{self.address}] Got error while trying approve token: {error}')
                        sleeping(f'[{self.address}] Error fault. Update after ')

        contract, w3 = self.get_contract(token_address, net_name)
        while True:
            balance, human_balance = self.get_balance(contract=contract)
            if amount:
                if balance > amount:
                    balance = amount
                elif amount > balance:
                    pass
                
            check_data = __check_allowance__()
            if check_data is not None:
                try:
                    tx_hash = self.send_transaction(check_data, net_name, approve=True)
                    if self.wait_until_tx_finished(tx_hash, net_name):
                        return
                    else:
                        sleeping(f'[{self.address}] Tx is failed. Will retry approve token ')
                except Exception as error:
                    logger.error(f'[{self.address}] Cant submit tx! Error: {error}')
                    sleeping(f'[{self.address}] Error fault. Update after ')
            else:
                return
    
    def sleeping(self):
        rand_time = random.randint(SETTINGS["TaskSleep"][0], SETTINGS["TaskSleep"][1])
        logger.info(f'[{self.address}] sleeping {rand_time} s')
        sleep(rand_time)

    def info(self, text: str):
        logger.info(f'[{self.address}] {text}')

    def error(self, text: str, error='None'):
        logger.error(f'[{self.address}] {text} | {error}')