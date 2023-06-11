from Connect import XTSConnect
from sys import platform
import time 
import os
import json
from Constants import *

import csv
import traceback

# funciton to write to CSV file the data for print statements
def save_print_to_csv(message, function_name, line_number):
    try:
        with open('print_log.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([message, function_name, line_number])
    except Exception as e:
        print(f"Error occurred while saving print to CSV: {str(e)}")


def xtsLogin(Credentials, Type):
    global api 
    try:    
        if Type == "intractive":
            api = XTSConnect(Credentials["API_KEY_intractive"], Credentials['API_SECRET_intractive'], "WEBAPI")
            api.interactive_login()
        else:
            api = XTSConnect(Credentials["API_KEY_marketfeed"], Credentials['API_SECRET_marketfeed'], "WEBAPI")
            api.marketdata_login()
        
        return api
    except Exception as e:
        while True:
            print(e)
            print("Error In Login Contact Arush, 7223018964")
            save_print_to_csv(str(e), 'xtsLogin', traceback.extract_stack()[-1].lineno)
            save_print_to_csv("Error In Login Contact Arush, 7223018964", 'xtsLogin', traceback.extract_stack()[-1].lineno)
            time.sleep(1)
            if platform == linux or platform == linux2:
                os.system(clear)
            elif platform == darwin:
                os.system(clear)
            elif platform == win32:
                os.system(cls)

def FindDiffBtwTwoStrikes(api, Token1, Token2):
    try:
        instruments = [
            {exchangeSegment: 2, ExchangeInstrumentId: Token1},
            {exchangeSegment: 2, ExchangeInstrumentId: Token2}
        ]
        print(instruments)
        save_print_to_csv(str(instruments), 'FindDiffBtwTwoStrikes', traceback.extract_stack()[-1].lineno)

        response = api.get_quote(
            Instruments=instruments,
            xtsMessageCode=1512,
            publishFormat='JSON'
        )
        save_print_to_csv(response , traceback.extract_stack()[-1].lineno)
        save_print_to_csv(str(response), 'FindDiffBtwTwoStrikes', traceback.extract_stack()[-1].lineno)

        print('Quote:', str(response[result][listQuotes]))
        save_print_to_csv("Quote: " + str(response['result']['listQuotes']), 'FindDiffBtwTwoStrikes', traceback.extract_stack()[-1].lineno)


        diff = json.loads(response[result][listQuotes][1]).get(LastTradedPrice) - json.loads(response[result][listQuotes][0]).get(LastTradedPrice)
        diff = round(diff, 2)
        save_print_to_csv("Diff" , diff, traceback.extract_stack()[-1].lineno)
        return diff
    except Exception as e:
        save_print_to_csv(e, traceback.extract_stack()[-1].lineno)
        return None


def FetchPositions(api):
    try:
        response = api.get_position_netwise().get(result).get(positionList)
        Positions = []
        for i in response:
            Positions.append({
                OptionContractName: i[TradingSymbol],
                Quantity: i[Quantity],
                QuantityToBeExecuted: i[Quantity],
                QuantityExecuted: "0",
                ProductType: i[ProductType],
                SellAverage: i[SellAveragePrice],
                Amount: int(float(i["NetAmount"])),
                AccountID: i[AccountID],
                ExchangeInstrumentId: i[ExchangeInstrumentId]
            })
            print(i)
            save_print_to_csv(str(i), 'FetchPositions', traceback.extract_stack()[-1].lineno)

        Positions.append({
            OptionContractName: "NIFTY 08JUN2023 CE 18900",
            Quantity: "-1000",
            QuantityToBeExecuted: "-1000",
            QuantityExecuted: "0",
            ProductType: "NRML",
            SellAverage: "4",
            Amount: "4000",
            AccountID: "PGDC",
            ExchangeInstrumentId: "45633"
        })
        return Positions
    except Exception as e:
        print(e)
        return []

 
def getIndexFromSymbol(symbol):
    try:
        if NIFTY in symbol and BANKNIFTY not in symbol and FINNIFTY not in symbol:
            return Nifty50
        if BANKNIFTY in symbol:
            return NiftyBank
        elif FINNIFTY in symbol:
            return NiftyFinService
    except Exception as e:
        print(e)
        return None

    
def ExpiryFromTradingSymbol(symbol):
    try:
        expiry = symbol.split(" ")[1]
        print(expiry)
        save_print_to_csv(expiry, 'ExpiryFromTradingSymbol', traceback.extract_stack()[-1].lineno)
        monthToNumber = {
            "JAN": "01",
            "FEB": "02",
            'MAR': "03",
            'APR': "04",
            'MAY': "05",
            'JUN': "06",
            'JUL': "07",
            'AUG': "08",
            'SEP': "09",
            'OCT': "10",
            'NOV': "11",
            'DEC': "12"
        }
        
        date = expiry[-4:len(expiry)] + "-" + monthToNumber.get(expiry[2:-4]) + "-" + expiry[0:2]
        print(date)
        save_print_to_csv(date, 'ExpiryFromTradingSymbol', traceback.extract_stack()[-1].lineno)
        return date
    except Exception as e:
        print(e)
        return None



def GetAllStrikeData(api, symbols):

    try:
        exchangesegments = [api.EXCHANGE_NSEFO]
        response = api.get_master(exchangeSegmentList=exchangesegments)
        file = response.get(result).split('\n')
        responseList = {}

        for symbol in symbols:
            expiry = ExpiryFromTradingSymbol(symbol)
            index = getIndexFromSymbol(symbol)
            OptionsList = []
            for i in file:
                if (OPTIDX in i) and (index in i) and (symbol.split(" ")[2] in i):
                    OptionsList.append(i)
            FinalSearchObject = []
            for i in OptionsList:
                list = i.split('|')
                FinalSearchObject.append({
                    ExchangeInstrumentId: list[1],
                    ExchangeSymbol: CreateFrontEndTradingSymbol(list[4])
                })
            responseList[symbol] = FinalSearchObject
        return responseList
    except Exception as e:
        print(e)
        return {}

def CreateFrontEndTradingSymbol(symbol):
    try:
        def CheckMonthPresent(symbol):
            for i in ["JAN", "FEB", 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']:
                if i in symbol:
                    return True
            return False

        if CheckMonthPresent(symbol) == True:
            if NIFTY in symbol and BANKNIFTY not in symbol and FINNIFTY not in symbol:
                return symbol[0:5] + " " + symbol[5:7] + " " + symbol[7:10] + " " + symbol[10:15] + " " + symbol[15:len(symbol)]
            if BANKNIFTY in symbol:
                return symbol[0:9] + " " + symbol[9:11] + " " + symbol[11:14] + " " + symbol[14:19] + " " + symbol[19:len(symbol)]
            elif FINNIFTY in symbol:
                return symbol[0:8] + " " + symbol[8:10] + " " + symbol[10:13] + " " + symbol[13:18] + " " + symbol[18:len(symbol)]
        if CheckMonthPresent(symbol) == False:
            if NIFTY in symbol and BANKNIFTY not in symbol and FINNIFTY not in symbol:
                return symbol[0:5] + " " + symbol[5:7] + " " + symbol[7:10] + " " + symbol[10:15] + " " + symbol[15:len(symbol)]
            if BANKNIFTY in symbol:
                return symbol[0:9] + " " + symbol[9:11] + " " + symbol[11:14] + " " + symbol[14:19] + " " + symbol[19:len(symbol)]
            elif FINNIFTY in symbol:
                return symbol[0:8] + " " + symbol[8:10] + " " + symbol[10:13] + " " + symbol[13:18] + " " + symbol[18:len(symbol)]
    except Exception as e:
        print(e)
        return None


def CheckAndTrade(api, DataStore, FetchedData, Qty):
    print("FetchedData:", FetchedData)
    save_print_to_csv(str(FetchedData), 'CheckAndTrade', traceback.extract_stack()[-1].lineno)
    print("DataStore:", DataStore)
    save_print_to_csv(str(DataStore), 'CheckAndTrade', traceback.extract_stack()[-1].lineno)
    try:
        print("Difference:")
        print(FetchedData.get(float(DataStore.get(ExchangeInstrumentId))).get(Touchline).get(LastTradedPrice) -
              FetchedData.get(float(DataStore.get(ShiftToExchangeInstrumentId))).get(Touchline).get(LastTradedPrice),
              float(DataStore.get(DesiredDifference)))
        print("")
        if FetchedData.get(float(DataStore.get(ExchangeInstrumentId))).get(Touchline).get(LastTradedPrice) - \
           FetchedData.get(float(DataStore.get(ShiftToExchangeInstrumentId))).get(Touchline).get(LastTradedPrice) >= \
           float(DataStore.get(DesiredDifference)):
            
            print(" ")
            
            print("Qty: ", Qty)
             
            if Qty < 0:
                RET = api.place_order(
                    exchangeSegment=api.EXCHANGE_NSEFO,
                    exchangeInstrumentID=int(DataStore.get(ExchangeInstrumentId)),
                    productType=api.PRODUCT_MIS,
                    orderType=api.ORDER_TYPE_MARKET,
                    orderSide=api.TRANSACTION_TYPE_BUY,
                    timeInForce=api.VALIDITY_DAY,
                    disclosedQuantity=0,
                    orderQuantity=abs(Qty),
                    limitPrice=0,
                    stopPrice=0,
                    orderUniqueIdentifier="454845",
                    clientID="PCGDE1569")
                print("RET:", RET)
                if RET.get(type) == success:
                    ret = api.place_order(
                        exchangeSegment=api.EXCHANGE_NSEFO,
                        exchangeInstrumentID=int(DataStore.get(ShiftToExchangeInstrumentId)),
                        productType=api.PRODUCT_MIS,
                        orderType=api.ORDER_TYPE_MARKET,
                        orderSide=api.TRANSACTION_TYPE_SELL,
                        timeInForce=api.VALIDITY_DAY,
                        disclosedQuantity=0,
                        orderQuantity=abs(Qty),
                        limitPrice=0,
                        stopPrice=0,
                        orderUniqueIdentifier="454845",
                        clientID="PCGDE1569")

                    if ret.get(type) == success:
                        DataStore[QuantityExecuted] = str(DataStore.get(QuantityToBeExecuted))
                        print("Order Placed")
                        print(ret)
                    else:
                        DataStore[QuantityExecuted] = "0"
                return DataStore
            else:
                DataStore[QuantityExecuted] = "0"
                return DataStore
        else:
            DataStore[QuantityExecuted] = "0"
            return DataStore
    except Exception as e:
        print(e)
        print("Error In Login Contact Arush, 7223018964")
        time.sleep(5)
        if platform == linux or platform == linux2:
            os.system(clear)
        elif platform == darwin:
            os.system(clear)
        elif platform == win32:
            os.system(cls)

        return False
