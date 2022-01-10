# Cryptocurrency Trading Algorithm

## Project Overview

This trading bot monitors the top thirty performing cryptocurrencies on https://coinmarketcap.com/trending-cryptocurrencies/ with the idea that many coins continue to increase in value after reaching this list.

## Files (In historicalDataAnalysis/)

* finalMarkets.csv: Contains smart contract addresses, exchanges, scam likelihood, buy and sell taxes, and relative liquidity available for each coin. Pulled from coinmarketcap.com and bscheck.eu.
* mainTest.py: Analyzes topBNB.csv to make fake trades based on historical price data.
* contractsBNB.csv: Contains contract addresses for each coin. Pulled from coinmarketcap.com
* getMarkets.py: Builds finalMarkets.csv using getTax, getExchange, getMarket, and getLiquidityPairs.
* topPerformers.py: Pulls data from https://coinmarketcap.com/trending-cryptocurrencies/ and builds topBNB.csv. Also pulls smart contract addresses for each coin.
* pricesBNB.csv: Has price data for coins that have fallen off the top thirty list.

## Files (In liveTrades/)

* liveTradeTests.py: The code required to buy and sell cryptocurrency using web3 and PancakeSwap.
