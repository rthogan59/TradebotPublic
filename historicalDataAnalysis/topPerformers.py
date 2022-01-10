from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import requests
from bs4 import BeautifulSoup
import pandas as pd
import schedule
import time
from datetime import datetime
from datetime import date
import csv
import json
from web3 import Web3

def getPancakePrice(address,web3Connection):

    tokenAddress = web3Connection.toChecksumAddress(address)
    tokenPrice = "https://deep-index.moralis.io/api/v2/erc20/" + tokenAddress + "/price?chain=bsc"

    erc20abi = """[
        {
            "constant": true,
            "inputs": [],
            "name": "name",
            "outputs": [
                {
                    "name": "",
                    "type": "string"
                }
            ],
            "payable": false,
            "stateMutability": "view",
            "type": "function"
        },
        {
            "constant": false,
            "inputs": [
                {
                    "name": "_spender",
                    "type": "address"
                },
                {
                    "name": "_value",
                    "type": "uint256"
                }
            ],
            "name": "approve",
            "outputs": [
                {
                    "name": "",
                    "type": "bool"
                }
            ],
            "payable": false,
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [],
            "name": "totalSupply",
            "outputs": [
                {
                    "name": "",
                    "type": "uint256"
                }
            ],
            "payable": false,
            "stateMutability": "view",
            "type": "function"
        },
        {
            "constant": false,
            "inputs": [
                {
                    "name": "_from",
                    "type": "address"
                },
                {
                    "name": "_to",
                    "type": "address"
                },
                {
                    "name": "_value",
                    "type": "uint256"
                }
            ],
            "name": "transferFrom",
            "outputs": [
                {
                    "name": "",
                    "type": "bool"
                }
            ],
            "payable": false,
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [],
            "name": "decimals",
            "outputs": [
                {
                    "name": "",
                    "type": "uint8"
                }
            ],
            "payable": false,
            "stateMutability": "view",
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [
                {
                    "name": "_owner",
                    "type": "address"
                }
            ],
            "name": "balanceOf",
            "outputs": [
                {
                    "name": "balance",
                    "type": "uint256"
                }
            ],
            "payable": false,
            "stateMutability": "view",
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [],
            "name": "symbol",
            "outputs": [
                {
                    "name": "",
                    "type": "string"
                }
            ],
            "payable": false,
            "stateMutability": "view",
            "type": "function"
        },
        {
            "constant": false,
            "inputs": [
                {
                    "name": "_to",
                    "type": "address"
                },
                {
                    "name": "_value",
                    "type": "uint256"
                }
            ],
            "name": "transfer",
            "outputs": [
                {
                    "name": "",
                    "type": "bool"
                }
            ],
            "payable": false,
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [
                {
                    "name": "_owner",
                    "type": "address"
                },
                {
                    "name": "_spender",
                    "type": "address"
                }
            ],
            "name": "allowance",
            "outputs": [
                {
                    "name": "",
                    "type": "uint256"
                }
            ],
            "payable": false,
            "stateMutability": "view",
            "type": "function"
        },
        {
            "payable": true,
            "stateMutability": "payable",
            "type": "fallback"
        },
        {
            "anonymous": false,
            "inputs": [
                {
                    "indexed": true,
                    "name": "owner",
                    "type": "address"
                },
                {
                    "indexed": true,
                    "name": "spender",
                    "type": "address"
                },
                {
                    "indexed": false,
                    "name": "value",
                    "type": "uint256"
                }
            ],
            "name": "Approval",
            "type": "event"
        },
        {
            "anonymous": false,
            "inputs": [
                {
                    "indexed": true,
                    "name": "from",
                    "type": "address"
                },
                {
                    "indexed": true,
                    "name": "to",
                    "type": "address"
                },
                {
                    "indexed": false,
                    "name": "value",
                    "type": "uint256"
                }
            ],
            "name": "Transfer",
            "type": "event"
        }
    ]"""

    contract = web3Connection.eth.contract(address=tokenAddress,abi=erc20abi)

    headers = {
        'x-api-key': ""
    }

    response = requests.request("GET",tokenPrice,headers=headers)

    resp = response.json()

    price = resp['nativePrice']['value']
    priceBNB = web3Connection.fromWei(int(price),'ether')
    priceUSD = resp['usdPrice']

    return(priceBNB,priceUSD)

def getContract(name,slug):
    site = 'https://coinmarketcap.com/currencies/' + slug
    r = requests.get(site)
    t = r.text
    soup = BeautifulSoup(t, features = 'html.parser')
    links = soup.findAll("a",href = True)
    for link in links:
        if 'bscscan.com' in link.get('href'):
            contract = link.get('href')
            contract = contract[contract.index('0x'):]
            if 's/' in contract: contract = contract[2:]
            if '#code#L1' in contract: contract = contract[-8]
            if '#code' in contract and "#code" not in name: contract = contract[:-5]
            if 'ken/' in contract: contract = contract[4:]
            if '#balances' in contract: contract = contract[:-9]
            if '#tokenAnalytics' in contract: contract = contract[:-15]
            if '#tokenInfo' in contract: contract = contract[:-10]
            if not str.isdigit(contract[-1]) and not str.isalpha(contract[-1]): contract = contract[:-1]
            return (contract,"Binance Smart Chain (BEP20)")
    return ("N/A","N/A")
    
    
def getTopPerformers():
        
    try:
        
        bsc = "https://speedy-nodes-nyc.moralis.io/88f9e10ecc7056e5ba53e173/bsc/mainnet"
        web3Connection = Web3(Web3.HTTPProvider(bsc))
        
        symbolLists = []
        #Read in existing price data
        with open("top.csv",'r') as file:
            csvreader = csv.reader(file)
            for row in csvreader:
                newSymbolList = []
                for i in range(1,len(row)):
                    if i%9 == 1:
                        newSymbolList.append(row[i]) 
                symbolLists.append(newSymbolList)
        
        coins = []
        contracts = []
        chains = []
        #Read in existing contract data
        with open('contracts.csv','r') as file:
            reader = csv.reader(file)
            for row in reader:
                coins.append(row[0])
                contracts.append(row[1])
                chains.append(row[2])
                
        
        now = datetime.now()
        now = now.strftime("%Y-%m-%d %H:%M:%S")
        
        with open("WBNBPrices.csv","a",newline="") as file:
            csvwriter = csv.writer(file)
            csvwriter.writerow([str(now),getPancakePrice("0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",web3Connection)[1]])
    
        site = "https://api.coinmarketcap.com/data-api/v3/cryptocurrency/spotlight?dataType=2&limit=30&rankRange=0&timeframe=24H"
        r = requests.get(site)
        t = r.text
        d = json.loads(t)
    
        
    
        
        with open("top.csv","a") as file:
            writer = csv.writer(file)
            symbolList = [now]
            
            for element in d['data']['gainerList']:
                name = element['name']
                price = element['priceChange']['price']
                priceChange1h = element['priceChange']['priceChange1h']
                priceChange24h = element['priceChange']['priceChange24h']
                priceChange7d = element['priceChange']['priceChange7d']
                priceChange30d = element['priceChange']['priceChange30d']
                volume = element['priceChange']['volume24h']
                slug = element['slug']
                symbolList.append(name)
                symbolList.append(price)
                symbolList.append(priceChange1h)
                symbolList.append(priceChange7d)
                symbolList.append(priceChange30d)
                symbolList.append(volume)
                symbolList.append(slug)
                
                #Get unknown contract addresses of coins
                if name not in coins:
                    with open("contracts.csv","a",newline="") as file:
                        
                        #Save between iterations
                        csvwriter = csv.writer(file)
                        contract = getContract(name,slug)
                        csvwriter.writerow([name,contract[0],contract[1]])
                        
                        #Save for current iteration
                        coins.append(name)
                        contracts.append(contract[0])
                        chains.append(contract[1])
                
                #Get pancake prices of bsc coins
                contractIndex = coins.index(name)
                contract = contracts[contractIndex]
                chain = chains[contractIndex]
                if chain == "Binance Smart Chain (BEP20)":
                    try:
                        pancakePrices = getPancakePrice(contract,web3Connection)
                        symbolList.append(pancakePrices[0])
                        symbolList.append(pancakePrices[1])
                    except:
                        symbolList.append("Error")
                        symbolList.append("Error")
                else:
                    symbolList.append("N/A")
                    symbolList.append("N/A")
                    
            
            writer.writerow(symbolList)
            
            #Add symbols and sites to lists for the current iteration
            newSymbolList = []
            for i in range(1,len(symbolList)):
                if i%9 == 1:
                    newSymbolList.append(symbolList[i]) 
            symbolLists.append(newSymbolList)
        
        
            
        #Get price of any bsc coins that were in the last thirty but aren't in this one
        prices = []
        if len(symbolLists) > 1:
            lastIterCoins = symbolLists[-2]
            currentIterCoins = symbolLists[-1]
            differences = list(set(lastIterCoins)-set(currentIterCoins))
            for coin in differences:
                chainIndex = coins.index(coin)
                chain = chains[chainIndex]
                contract = contracts[chainIndex]
                if chain == "Binance Smart Chain (BEP20)":
                    #Retrieve PancakeSwap Price
                    try:
                        pancakePrice = getPancakePrice(contract,web3Connection)
                        prices.append((now,coin,pancakePrice[0],pancakePrice[1]))
                    except:
                        prices.append((now,coin,"Error","Error"))
        
        #Append price data to prices.csv
        with open("prices.csv","a",newline="") as file:
            csvwriter = csv.writer(file)
            for price in prices:
                csvwriter.writerow([price[0],price[1],price[2],price[3]])
    
    except:
        print("Error at time " + str(now))
        pass
    


schedule.every(10).minutes.do(getTopPerformers)

while True:
    schedule.run_pending()
    time.sleep(30)

#Need to check:
    #bscheck.eu results
    #Whether a WBNB pair exists on pancakeswap