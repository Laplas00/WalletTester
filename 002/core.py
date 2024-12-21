from multiprocessing import Pool
from bip_utils import Bip39MnemonicGenerator, Bip39WordsNum, Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
from config import API_KEY
import requests
import time
import os
import json



class WalletGenerator:
    def __init__(self):
        """
        Initialize a WalletGenerator object to create wallets from BIP39 words.
        """
        self.mnemonic_generator = Bip39MnemonicGenerator()
        print("[INFO] WalletGenerator initialized.")
    
    def generate_ETH_wallet_from_12_words(self):
        mnemonic = self.mnemonic_generator.FromWordsNumber(Bip39WordsNum.WORDS_NUM_12)
        print(f"[INFO] Generated mnemonic: {mnemonic}")
        seed_bytes = Bip39SeedGenerator(mnemonic).Generate()
        bip44_mst_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.ETHEREUM)
        bip44_acc_ctx = bip44_mst_ctx.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0)
        wallet = {"mnemonic": str(mnemonic),
                "address": bip44_acc_ctx.PublicKey().ToAddress(),
                "public_key": bip44_acc_ctx.PublicKey().RawCompressed().ToHex(),
                "private_key": bip44_acc_ctx.PrivateKey().Raw().ToHex()}
        
        print(f"[INFO] Generated wallet address: {wallet['address']}")
        return wallet


def get_wallet_balance(address, api_key):
    url = f"https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest&apikey={api_key}"
    print(f"[INFO] Fetching balance for address: {address}")
    response = requests.get(url)
    if response.status_code != 200:
        return None
    elif response.json()['message'] == 'OK':
        data = response.json()
        return data
    elif response.json()['message'] == 'NOTOK':
        print(response.json())
        time.sleep(6000)
        


def get_wallet_transactions(address, api_key):
    url = f"https://api.etherscan.io/api?module=account&action=txlist&address={address}&startblock=0&endblock=99999999&sort=asc&apikey={api_key}"
    response = requests.get(url)

    if response.status_code != 200:
        return None

    response_data = response.json()
    if response_data['status'] == '1' and response_data['message'] == 'OK':
        # print(f"[INFO] Transactions fetched successfully for {address}.")
        return response_data['result']
    elif response_data['status'] == '0' and response_data['message'] == 'No transactions found':
        return []
    else:
        return None

def process_task(func_and_args):
    func, args = func_and_args
    return func(*args)


def wallet_brootforce(wallet_generator, api_key):
    wallet = wallet_generator.generate_ETH_wallet_from_12_words()
    balance = get_wallet_balance(wallet["address"], api_key)
    transactions = get_wallet_transactions(wallet['address'], api_key)
    return {
        'wallet':wallet,
        'balance':balance,
        'transactions':transactions,
    }


def save_dict_to_json(data, filename="data.json"):
    if not isinstance(data, dict):
        raise ValueError("Input data must be a dictionary.")
    
    if os.path.exists(filename):
        with open(filename, "r") as file:
            try:
                json_data = json.load(file)
                if not isinstance(json_data, list):
                    raise ValueError(f"JSON file must contain a list, found: {type(json_data).__name__}")
            except json.JSONDecodeError:
                json_data = []
    else:
        json_data = []

    json_data.append(data)
    with open(filename, "w") as file:
        json.dump(json_data, file, indent=4)
        print(f"[INFO] Data appended to {filename} successfully.")



def main():
    wallet_generator = WalletGenerator()
    api_key1 = ...
    api_key2 = ...
    api_key3 = ...

    # here we can add different api, to use for each stream different api_key

    loops = 0
    looping = True
    while looping:
        try:            
            tasks = [
                    (wallet_brootforce, (wallet_generator, api_key1)),
                    (wallet_brootforce, (wallet_generator, api_key2)),
                    (wallet_brootforce, (wallet_generator, api_key3)),
                    (wallet_brootforce, (wallet_generator, api_key1)),
                    (wallet_brootforce, (wallet_generator, api_key2)),
                    (wallet_brootforce, (wallet_generator, api_key3)),
                ]
            
            with Pool(processes=2) as pool:  # Set 'processes' to the number of$
                results = pool.map(process_task, tasks)

            print('---- Time to results ----')
            for completed in results:

                # statements to save wallet into db
                balance_statement = completed['balance']['result'] != '0'
                transactions_statement = completed['transactions'] not in ([], None)

                if balance_statement or transactions_statement:
                    print('\t\t\t\tLittle win')
                    save_dict_to_json(completed)

                print(completed['wallet'])
                print(completed['balance'])
                
                
            loops += 1

            print('|'*40)
            # time.sleep(1)
            # break

        except KeyboardInterrupt:
            break

        # except error as e:
        #     print('restart')
        #     continue



if __name__ == "__main__":
    main()
