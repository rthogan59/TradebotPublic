import csv
from datetime import datetime
from os import times_result
import pytrends
import time as t
from scipy.optimize import minimize

def main(csvFile,coinPercentage,sellSoonTime,normalSellTime,buyCount):

    #Create list of times, symbols, and percent changes from the csv file
    topEarners = {}
    timeList = []
    symbolLists = []
    changeLists = []
    change1HLists = []
    change7DLists = []
    change30DLists = []
    volumeLists = []
    slugLists = []
    bnbPriceLists = []
    usdPriceLists = []

    zeroCount = 0
    coins = []
    contracts = []
    chains = []
    audits = []
    scams = []
    buyTaxes = []
    sellTaxes = []
    exchanges = []
    markets = []
    with open('finalMarkets.csv','r') as file:
        reader = csv.reader(file)
        for row in reader:
            coins.append(row[0])
            contracts.append(row[1])
            chains.append(row[2])
            scams.append(row[3])
            buyTaxes.append(row[4])
            sellTaxes.append(row[5])
            if len(row) > 6:
                count = 6
                newExchanges = []
                newMarkets = []
                while "/" not in row[count]:
                    newExchanges.append(row[count])
                    count += 1
                
                for i in range(count,len(row),2):
                    newMarkets.append((row[i],row[i+1]))
                
                exchanges.append(newExchanges)
                markets.append(newMarkets)
            else:
                exchanges.append([])
                markets.append([])

    with open(csvFile,'r') as file:
        csvreader = csv.reader(file)
        for row in csvreader:
            newSymbolList = []
            newChangeList = []
            newVolumeList = []
            new1HList = []
            new7DList = []
            new30DList = []
            newSlugList = []
            newBNBPriceList = []
            newUSDPriceList = []
            timeList.append(row[0])
            for i in range(1,len(row)):
                if i%9 == 1:
                    newSymbolList.append(row[i]) 
                elif i%9 == 2:
                    newChangeList.append(row[i])
                elif i%9 == 3:
                    new1HList.append(row[i])
                elif i%9 == 4:
                    new7DList.append(row[i])
                elif i%9 == 5:
                    new30DList.append(row[i])
                elif i%9 == 6:
                    newVolumeList.append(row[i])
                elif i%9 == 7:
                    newSlugList.append(row[i])
                elif i%9 == 8:
                    newBNBPriceList.append(row[i])
                elif i%9 == 0:
                    newUSDPriceList.append(row[i])

            
            symbolLists.append(newSymbolList)
            changeLists.append(newChangeList)
            change1HLists.append(new1HList)
            change7DLists.append(new7DList)
            change30DLists.append(new30DList)
            volumeLists.append(newVolumeList)
            slugLists.append(newSlugList)
            bnbPriceLists.append(newBNBPriceList)
            usdPriceLists.append(newUSDPriceList)


    #Find out what coins I would have bought
    gasAmount = .9
    tradesMade = 0
    availableCapital = 1000
    investedCapital = 0
    buyAmount = min(2000,availableCapital / coinPercentage)
    boughtCoins = set()
    openPositions = []
    dontBuy = []
    dontTrack = ["Mars Space X","Bankless DAO"]
    for i in range(len(scams)):
        if scams[i] == "True":
            dontTrack.append(coins[i])

    for i in range(len(buyTaxes)):
        if buyTaxes[i] != "0" or sellTaxes[i] != "0":
            dontTrack.append(coins[i])

    residualPriceListTimes = []
    residualPriceListSymbols = []
    residualPriceListBNB = []
    residualPriceListUSD = []
    residualPriceList = []
    with open("pricesBNB.csv","r") as file:
        csvreader = csv.reader(file)
        for row in csvreader:
            residualPriceList.append(row)
            residualPriceListTimes.append(row[0])
            residualPriceListSymbols.append(row[1])
            residualPriceListBNB.append(row[2])
            residualPriceListUSD.append(row[3])

    for time in range(len(timeList)):
        #if time % 400 == 0:
        #    dontTrack = []
        
        dontBuy = []
        
        if time % 720 == 0:
            positionsToSell = []
            for position in openPositions:
                symbol = position[0]
                timeBought = position[1]
                percentageBought = position[2]
                cost = position[4]
                index = symbolLists[time-1].index(symbol)
                currentPercentage = float(usdPriceLists[time-1][index])*.99
                profit = (cost-gasAmount)*(float(currentPercentage)/float(percentageBought))
                difference = (float(currentPercentage))/(float(percentageBought))

                if symbol in topEarners:
                    topEarners[symbol] += profit-(cost+gasAmount)
                else:
                    topEarners[symbol] = profit-(cost+gasAmount)

                availableCapital += profit
                investedCapital -= cost
                positionsToSell.append(position)

            for position in positionsToSell:
                openPositions.remove(position)
        

        bought = []
        sold = []
        for symbol in symbolLists[time]:
            #Check if coin is on the Binance chain
            #Add contract if it's not there
            isBinance = False
            name = symbol.split("(")[0]
            if name[-1] == " ": name = name[:-1]
            if name in coins:
                index = coins.index(name)
                chain = chains[index]
                contract = contracts[index]
                if chain == "Binance Smart Chain (BEP20)":
                    isBinance = True
            
            #Check that coin isn't an error and that it has a USDT pair
            notError = False
            if usdPriceLists[time][symbolLists[time].index(symbol)] != "Error":
                notError = True
                index = coins.index(symbol)
                coinMarkets = markets[index]
                exchange = exchanges[index]
                #notError = (all(float(x)==0 for x in [pair[1] for pair in coinMarkets]) and len(exchange) > 2)
                #Check exchange values
                #bnbVals = []
                #for i in range(len(coinMarkets)):
                #    if "USDT" in coinMarkets[i][0]:
                #        bnbVals.append(coinMarkets[i][1])
                #if "PancakeSwap (V2)" in exchange:
                #    pancakeIndex = exchange.index("PancakeSwap (V2)")
                #    if pancakeIndex < len(exchange)/3 and len(exchange) > 6:
                #        notError = True
                #    else:
                #        notError = False
                #else:
                #    notError = False
                #notError = any(float(x)>300 for x in bnbVals) 
                valid = ["Oddz","Dibs Share","YAY Games","Rainicorn","Meta World Game","Zenon","The Winkyverse","RPS League","GovWorld","USD Coin","TerraUSD","Tether","TrueUSD","Binance USD","PancakeSwap","ThreeFold","Formation Fi","Turtle Racing","Surviving Soldiers","Uniswap","Elrond","Cosmos","BitTorrent","Chainlink","Velas","Cryptogodz","8PAY","Multiverse","MetaRacers","BALI TOKEN","GoldMiner","ProximaX","Age Of Knights","The Parallel","Orakler","POOMOON","Fuse Network","Kryxivia","AgeOfGods","EQIFI","MILC Platform","Xircus","Lovelace World","XenophonDAO","Planet Sandbox","Cherry","Offshift","MetaGods","CrazyMiner","Zodiacs","Bomb Money"]

                if symbol in valid:
                    notError = True
                else:
                    notError = False
            #Execute trades
            #Dont Buy Count is the biggest variable
            #Range from 3 to 15
            if notError and availableCapital > buyAmount and buyAmount > 100 and symbol not in dontTrack and dontBuy.count(symbol) < buyCount and isBinance:
                tradesMade += 1
                boughtCoins.add(symbol)
                index = symbolLists[time].index(symbol)
                
                sellSoonFlag = False
                if time > 1:
                    if symbol not in symbolLists[time-1]:
                        sellSoonFlag = True
                
                bought.append(symbol)

                dontBuy.append(symbol)
                
                #Only buy coins that are > the top two on the list once for the first 200 timeframes
                if symbolLists[time].index(symbol) >= 10 and time < 100:
                    dontTrack.append(symbol)
                
                if symbolLists[time].index(symbol) >= 10:
                    dontTrack.append(symbol)

                cost = buyAmount

                openPositions.append((symbol,timeList[time],float(usdPriceLists[time][index])*.99,False,cost))
                availableCapital -= (buyAmount*1.01 + gasAmount)
                investedCapital += buyAmount
                buyAmount = min(2000,availableCapital / (coinPercentage*.28))

        #Check for selling conditions
        positionsToSell = []
        for position in openPositions:
            symbol = position[0]
            timeBought = position[1]
            percentageBought = position[2]
            sellSoonFlag = position[3]
            cost = position[4]

            timeBought = datetime.strptime(timeBought, '%Y-%m-%d %H:%M:%S')
            currentTime = datetime.strptime(timeList[time], '%Y-%m-%d %H:%M:%S')
            timeDifference = (currentTime - timeBought).total_seconds()
            
            if sellSoonFlag == True and timeDifference > sellSoonTime:
                index = symbolLists[time-1].index(symbol)
                currentPercentage = usdPriceLists[time-1][index]
                downgrade = 0
                try:
                    index = symbolLists[time].index(symbol)
                    currentPercentage = usdPriceLists[time][index]
                except:
                    downgrade = 0.2
                    pass
                
                profit = (cost-gasAmount)*(float(currentPercentage)/float(percentageBought) - downgrade)
                difference = float(currentPercentage)/(float(percentageBought))

                if symbol in topEarners:
                    topEarners[symbol] += profit-cost
                else:
                    topEarners[symbol] = profit-cost

                
                #if symbol == "2030 Floki":
                #    print(symbol + " bought at " + percentageBought + " at time " + position[1])
                #    print(symbol + " sold at " + currentPercentage + " at time " + timeList[time])
                #    print(difference)
                #    print(availableCapital)
                #    print(cost)
                #    print()
                sold.append((symbol,profit))

                positionsToSell.append(position)
                availableCapital += profit
                investedCapital -= cost
                buyAmount = min(2000,availableCapital / (coinPercentage*.28))

            elif timeDifference > normalSellTime or symbol not in symbolLists[time]:
                index = symbolLists[time-1].index(symbol)
                currentPercentage = float(usdPriceLists[time-1][index])*.99
                try:        
                    index = symbolLists[time].index(symbol)
                    currentPercentage = usdPriceLists[time][index]
                    if currentPercentage == "Error":
                        print(symbol)
                        print(time)
                except:
                    #Update current price to reflect price listed in pricesBNB.csv
                    index = residualPriceListTimes.index(timeList[time])
                    while(residualPriceListSymbols[index] != symbol):
                        index += 1
                    currentPercentage = residualPriceListUSD[index]

                profit = (cost-gasAmount)*(float(currentPercentage)/float(percentageBought))
                difference = float(currentPercentage)/(float(percentageBought))

                if symbol in topEarners:
                    topEarners[symbol] += profit-(cost+gasAmount)
                else:
                    topEarners[symbol] = profit-(cost+gasAmount)
                
                #if symbol == "2030 Floki":
                #    print(symbol + " bought at " + percentageBought + " at time " + position[1])
                #    print(symbol + " sold at " + currentPercentage + " at time " + timeList[time])
                #    print(difference)
                #    print(availableCapital)
                #    print(cost)
                #    print()
                sold.append((symbol,profit))

                positionsToSell.append(position)
                availableCapital += profit
                investedCapital -= cost
                buyAmount = min(2000,availableCapital / (coinPercentage*.28))
        '''
        with open("trades.txt","a") as file:
            file.write("Time: " + timeList[time] + "\n")
            file.write("BOUGHT: ")
            for symbol in bought:
                file.write(symbol + " ")
            file.write("\n")
            profit = 0
            file.write("Sold: ")
            for symbol in sold:
                profit += symbol[1]
                file.write(symbol[0] + " ")
            file.write("\n")
            file.write("Profit for this timeframe: " + str(profit) + "\n")
            file.write("Total capital: " + str(availableCapital+investedCapital) + "\n")
            file.write("Buy Amount: " + str(buyAmount) + "\n")
            file.write("\n")
            '''
        for position in positionsToSell:
            openPositions.remove(position)
            
    #Close out all positions
    endProfit = 0
    for position in openPositions:
        symbol = position[0]
        timeBought = position[1]
        percentageBought = position[2]
        cost = position[4]
        index = symbolLists[len(timeList)-1].index(symbol)
        currentPercentage = float(usdPriceLists[time][index])*.99
        profit = (cost-gasAmount)*(float(currentPercentage)/float(percentageBought))
        difference = (float(currentPercentage))/(float(percentageBought))

        if symbol in topEarners:
            topEarners[symbol] += profit-(cost+gasAmount)
        else:
            topEarners[symbol] = profit-(cost+gasAmount)

        endProfit += profit
        availableCapital += profit
        investedCapital -= cost
    '''
    with open("trades.txt","a") as file:
        file.write("Closing out positions \n")
        file.write("Profit for this timeframe: " + str(endProfit) + "\n")
        file.write("Total capital: " + str(availableCapital))
    '''

    openPositions = []

    print(tradesMade)
    print(availableCapital)
    #print(boughtCoins)
    #print(dict(sorted(topEarners.items(), key=lambda item: item[1])))

    #sum = 0
    #for earner in topEarners.items():
    #    sum += earner[1]
    #print(sum)
    #print(topEarners)
    #with open('boughtCoins.txt','w') as file:
    #    for coin in boughtCoins:
    #        file.write(coin + "\n")

#coinPercentage,sellSoonTime,normalSellTime,buyCount,
main("topBNB.csv",5,4000,4000,8)
