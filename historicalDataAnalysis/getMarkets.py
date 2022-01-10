import csv
import requests
from bs4 import BeautifulSoup
import json
from os import write
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import urllib
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import csv
import time
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

#Check if "Cannot find LP infos" or "You may have troubles to buy/sell" in bscheck.eu

def getTax(contract):
    capa = DesiredCapabilities.CHROME
    capa["pageLoadStrategy"] = "none"

    op = webdriver.ChromeOptions()
    op.add_argument('ignore-certificate-errors')
    op.add_argument('headless')
    driver = webdriver.Chrome(desired_capabilities = capa,options=op)
    wait = WebDriverWait(driver, 60)
    url = "https://www.bscheck.eu/bsc/" + contract
    driver.get(url)
    wait.until(EC.presence_of_element_located((By.ID, 'report_tile_result')))
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()
    t = soup.prettify()
    isScam = True
    
    if "Sell seems to be OK" in t:
        isScam = False
    
    buyTax = "N/A"
    sellTax = "N/A"
    if isScam == False:
        buyTax = re.findall(r".uy Tax : \d*\.?\d*%",t)[0][10:-1]
        sellTax = re.findall(r".ell Tax : \d*\.?\d*%",t)[0][11:-1]
    
    return [isScam,buyTax,sellTax]

def getExchange(slug):
    site = "https://api.coinmarketcap.com/data-api/v3/cryptocurrency/market-pairs/latest?slug=" + slug + "&start=1&limit=100&category=spot&sort=cmc_rank_advanced"
    r = requests.get(site)
    t = r.text
    d = json.loads(t)
    exchanges = []
    for exchange in d['data']['marketPairs']:
        exchanges.append(exchange['exchangeName'])
    return exchanges

def getMarket(slug):
    site = "https://api.coinmarketcap.com/data-api/v3/cryptocurrency/market-pairs/latest?slug=" + slug + "&start=1&limit=100&category=spot&sort=cmc_rank_advanced"
    r = requests.get(site)
    t = r.text
    d = json.loads(t)
    pairs = []
    for pair in d['data']['marketPairs']:
        pairs.append(pair['marketPair'])
    return pairs

def getLiquidityPairs(slug):
    site = "https://api.coinmarketcap.com/data-api/v3/cryptocurrency/market-pairs/latest?slug=" + slug + "&start=1&limit=100&category=spot&sort=cmc_rank_advanced"
    r = requests.get(site)
    t = r.text
    d = json.loads(t)
    pairs = []
    for pair in d['data']['marketPairs']:
        pairs.append(pair['marketPair'])
        pairs.append(pair['effectiveLiquidity'])
    return pairs


contractsList = []
with open("finalMarkets.csv","r") as file:
    csvreader = csv.reader(file)
    for row in csvreader:
        contractsList.append(row)
'''
newList = []
for row in contractsList:
    if len(row) == 3:
        newList.append(row + ['N/A','N/A','N/A'])
    else:
        newList.append(row)

with open('contractsBNB.csv','w',newline='') as file:
    csvwriter = csv.writer(file)
    for contract in newList:
        csvwriter.writerow(contract)
'''
newContracts = []
with open("newContractsBNB.csv","r") as file:
    csvreader = csv.reader(file)
    for row in csvreader:
        newContracts.append(row)


symbolLists = []
slugLists = []
with open("topBNB.csv","r") as file:
    csvreader = csv.reader(file)
    for row in csvreader:
        for i in range(1,len(row)):
            if i%9 == 1:
                symbolLists.append(row[i])
            if i%9 == 7:
                slugLists.append(row[i])

'''
for contract in contractsList:
    with open("finalMarkets1.csv","a",newline="") as file:
        csvwriter = csv.writer(file)
        csvwriter.writerow(contract)
'''
for contract in newContracts:
    symbol = contract[0]

    if contract[2] == "Binance Smart Chain (BEP20)":
        slug = slugLists[symbolLists.index(symbol)]
        pairs = getLiquidityPairs(slug)
        taxInfo = getTax(contract[1])
        print("Tax Info for " + contract[0] + ": " + str(taxInfo[0]) + " " + str(taxInfo[1]) + " " + str(taxInfo[2]))
        exchanges = getExchange(slug)
        with open("finalMarkets1.csv","a",newline="") as file:
            csvwriter = csv.writer(file)
            csvwriter.writerow(contract + taxInfo + exchanges + pairs)
        time.sleep(150)
    else:
        with open("finalMarkets1.csv","a",newline="") as file:
            csvwriter = csv.writer(file) 
            csvwriter.writerow(contract + ['N/A','N/A','N/A'])

'''
goodContractsList = []
workContractsList = []
with open("finalMarkets.csv","r") as file:
    csvreader = csv.reader(file)
    for row in csvreader:
        if len(list(row)) > 6:
            goodContractsList.append(list(row))
        else:
            workContractsList.append(list(row))

symbolLists = []
slugLists = []
with open("topBNB.csv","r") as file:
    csvreader = csv.reader(file)
    for row in csvreader:
        for i in range(1,len(row)):
            if i%9 == 1:
                symbolLists.append(row[i])
            if i%9 == 7:
                slugLists.append(row[i])




with open("finalMarkets1.csv","w",newline="") as file:
    csvwriter = csv.writer(file)
    for contract in goodContractsList:
        csvwriter.writerow(contract)

    for contract in workContractsList:
        symbol = contract[0]
        try:
            slug = slugLists[symbolLists.index(symbol)]
            markets = getMarket(slug)
            csvwriter.writerow(contract + markets)
        except:
            csvwriter.writerow(contract)

'''