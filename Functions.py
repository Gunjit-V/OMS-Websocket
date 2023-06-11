        

from Connect import XTSConnect
from sys import platform
import time 
import os
import json

def xtsLogin(Credentials, Type):
    global api 
    try:    
        if(Type =="intractive"):
         api = XTSConnect(Credentials["API_KEY_intractive"], Credentials['API_SECRET_intractive'], "WEBAPI")
         api.interactive_login()
        else :
         api = XTSConnect(Credentials["API_KEY_marketfeed"], Credentials['API_SECRET_marketfeed'], "WEBAPI")
         api.marketdata_login()
        
        return api
    except Exception as e :
        while True:
            print(e)
            print("Error In Login Contact Arush , 7223018964")
            time.sleep(1)
            if platform == "linux" or platform == "linux2":
    # linux
                os.system('clear')
            elif platform == "darwin":
    # OS X     
                os.system('clear')
            elif platform == "win32":
    # Windows...
                os.system('cls')
            

def FindDiffBtwTwoStrikes(api ,Token1 , Token2 ):
    instruments = [
    {'exchangeSegment': 2, 'exchangeInstrumentID': Token1},
    {'exchangeSegment': 2, 'exchangeInstrumentID': Token2}
    ]
    print(instruments)
    response = api.get_quote(
    Instruments=instruments,
    xtsMessageCode=1512,
    publishFormat='JSON')
    print(response)
    print('Quote :',str( response['result']['listQuotes']))

    diff =  json.loads(response['result']['listQuotes'][1]).get('LastTradedPrice') -json.loads(response['result']['listQuotes'][0]).get('LastTradedPrice')
    diff = round(diff ,2)
    return diff


def FetchPositions(api):
    response =   api.get_position_netwise().get('result').get('positionList')
    Positions =[]
    for i in response:
        if(i['Quantity']!="0"):
          Positions.append({
            "OptionContractName" : i["TradingSymbol"],
            "Quantity" : i["Quantity"],
            "QuantityToBeExecuted":i["Quantity"],
            "QuantityExecuted":"0",
            "ProductType":i["ProductType"],
            "SellAverage":i["SellAveragePrice"],
            "Amount":int(float(i["NetAmount"])),
            "loop":'False',
            "AccountID":i["AccountID"],
            "ExchangeInstrumentId":i["ExchangeInstrumentId"]
            
            }
        )
        print(i)
    # Positions.append({
    #         "OptionContractName" : "NIFTY 08JUN2023 CE 18900",
    #         "Quantity" :"-1000",
    #         "QuantityToBeExecuted":"-1000",
    #         "QuantityExecuted": "0",
    #         "ProductType":"NRML",
    #         "SellAverage":"4",
    #         "Amount":"4000",
    #         "AccountID":"PGDC",
    #         "ExchangeInstrumentId":"45633"
    #         }
    #     )
    return  Positions
 
def getIndexFromSymbol(symbol):
    if(('NIFTY' in symbol) and ('BANKNIFTY' not in symbol )and ('FINNIFTY' not in symbol)):
        return 'Nifty 50'
    if('BANKNIFTY' in symbol ):
        return 'Nifty Bank'
    elif('FINNIFTY' in symbol ):
        return 'Nifty Fin Service'
    
    
def ExpiryFromTradingSymbol(symbol):
    expiry = symbol.split(" ")[1]
    # print( symbol.split(" ")[2])
    print(expiry)
    monthToNumber ={
        "JAN":"01",
        "FEB":"02",
        'MAR':"03",
        'APR':"04",
        'MAY':"05",
        'JUN':"06",
        'JUL':"07",
        'AUG':"08",
        'SEP':"09",
        'OCT':"10",
        'NOV':"11",
        'DEC':"12"
    }
    
    date = expiry[-4:len(expiry)]+ "-" +monthToNumber.get(expiry[2:-4]) +"-"+ expiry[0:2]

    print(date)
    return date

def GetAllStrikeData(api , symbols):
    exchangesegments = [ api.EXCHANGE_NSEFO]
    response = api.get_master(exchangeSegmentList=exchangesegments)
    
    file =response.get('result').split('\n')
    responseList = {}
    
    for symbol in symbols:
        # print("Inside: " + symbol)
        expiry =ExpiryFromTradingSymbol(symbol)
        index = getIndexFromSymbol(symbol)
      
        
        OptionsList =[]
        for i in file: 
            #  if ("OPTIDX" in i) and (expiry in i ) and ( index in i) and ( symbol.split(" ")[2] in i):
             if ("OPTIDX" in i) and ( index in i) and ( symbol.split(" ")[2] in i):
             
                OptionsList.append(i)
   
        FinalSearchObject = []
        for i in OptionsList :
            # print(i)
            list = i.split('|')
            FinalSearchObject.append({
                "ExchangeInstrumentId":list[1] , "ExchangeSymbol":CreateFrontEndTradingSymbol(list[4])
            })
        #   "FINNIFTY2352319550CE" "NIFTY23MAY15750PE"
        responseList[symbol] = FinalSearchObject
        # responseList.append("symbol":{FinalSearchObject})
       
    return responseList

def CreateFrontEndTradingSymbol(symbol): 
    def CheckMonthPresent(symbol):
        for  i  in ["JAN","FEB",'MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC'] :
           if i in symbol:
               return True
            
        return False
    # "NIFTY23MAY15750PE"
    NumberToMonth ={
        "1":"JAN",
        "2":"FEB",
        '3':"MAR",
        '4':"APR",
        '5':"MAY",
        '6':"JUN",
        '7':"JUL",
        '8':"AUG",
        '9':"SEP",
        '10':"OCT",
        '11':"NOV",
        '12':"DEC"
    }
    if(CheckMonthPresent(symbol) ==True):
          if(('NIFTY' in symbol) and ('BANKNIFTY' not in symbol )and ('FINNIFTY' not in symbol)):
             return str(symbol[0:5]+" " + symbol[5:7] +" "+symbol[7:10] + " "+symbol[10:15] +" "+ symbol[15:len(symbol)])
          if('BANKNIFTY' in symbol ):
            return str(symbol[0:9]+" " + symbol[9:11 ] + " " + symbol[11:14]+ " " + symbol[14:19]+ " "+symbol[19:len(symbol)])
          elif('FINNIFTY' in symbol ):
           return str(symbol[0:8]+" " + symbol[8:10] +" "+symbol[10:13] + " "+symbol[13:18] +" "+ symbol[18:len(symbol)])
    if(CheckMonthPresent(symbol) ==False):
          if(('NIFTY' in symbol) and ('BANKNIFTY' not in symbol )and ('FINNIFTY' not in symbol)):
             return str(symbol[0:5]+" "+symbol[5:7]  +" " + symbol[8:10] +" " + NumberToMonth.get(symbol[7:8])+" "+symbol[10:15] +" "+ symbol[15:len(symbol)])
          if('BANKNIFTY' in symbol ):
            return str(symbol[0:9] + " "+ symbol[9:11 ]+" "+ symbol[13:14] + " " + NumberToMonth.get(symbol[11:13])+ " " + symbol[14:19]+ " "+symbol[19:len(symbol)])
          elif('FINNIFTY' in symbol ):
           return str(symbol[0:8]+" " + symbol[8:10]  +" " +symbol[12:13]+" "+ NumberToMonth.get(symbol[10:12]) + " "+symbol[13:18] +" "+ symbol[18:len(symbol)])

def CheckAndTrade(api , DataStore , FetchedData  , Qty  ):
        print("FetchedData:",FetchedData)
        print("DataStore:" ,DataStore)
        try:
         print("Difference:")
         print(FetchedData.get(float(DataStore.get('ExchangeInstrumentId'))).get('Touchline').get('LastTradedPrice')-FetchedData.get(float(DataStore.get('ShiftToExchangeInstrumentId'))).get('Touchline').get('LastTradedPrice') , float(DataStore.get('DesiredDifference')))
         print("")
         if(FetchedData.get(float(DataStore.get('ExchangeInstrumentId'))).get('Touchline').get('LastTradedPrice')-FetchedData.get(float(DataStore.get('ShiftToExchangeInstrumentId'))).get('Touchline').get('LastTradedPrice') <=float( DataStore.get('DesiredDifference'))):
            
            print(" ")
            Qty = abs(Qty)
            print("Qty: ",Qty)
            # Config = open('Config.json')
            # Config = json.load(Config)
            
            Config ={"QuantitySlicer":1000}
            while(Qty >1800):
                RET = api.place_order(
                exchangeSegment=api.EXCHANGE_NSEFO,
                exchangeInstrumentID=int(DataStore.get('ExchangeInstrumentId')),
                productType=api.PRODUCT_NRML,
                orderType=api.ORDER_TYPE_MARKET,
                orderSide=api.TRANSACTION_TYPE_BUY,
                timeInForce=api.VALIDITY_DAY,
                disclosedQuantity=0,
                orderQuantity=abs(1800),
                limitPrice=0,
                stopPrice=0,
                orderUniqueIdentifier="454845",
                clientID="PCGDE1569")
                print("RET:",RET)
                if(RET.get('type')=='success'):
                
                
                 ret = api.place_order(
                exchangeSegment=api.EXCHANGE_NSEFO,
                exchangeInstrumentID=int(DataStore.get('ShiftToExchangeInstrumentId')),
                productType=api.PRODUCT_NRML,
                orderType=api.ORDER_TYPE_MARKET,
                orderSide=api.TRANSACTION_TYPE_SELL,
                timeInForce=api.VALIDITY_DAY,
                disclosedQuantity=0,
                orderQuantity=abs(1800),
                limitPrice=0,
                stopPrice=0,
                orderUniqueIdentifier="454845",
                clientID="PCGDE1569")
                 

                 if(ret.get('type') == 'success'):
                  DataStore['QuantityExecuted'] =str(int(float(DataStore['QuantityExecuted'])-1800))
                  print("Order Placed")
                  print(ret)
                  Qty = Qty-1800
            if(Qty > 0):
             

              RET = api.place_order(
                exchangeSegment=api.EXCHANGE_NSEFO,
                exchangeInstrumentID=int(DataStore.get('ExchangeInstrumentId')),
                productType=api.PRODUCT_NRML,
                orderType=api.ORDER_TYPE_MARKET,
                orderSide=api.TRANSACTION_TYPE_BUY,
                timeInForce=api.VALIDITY_DAY,
                disclosedQuantity=0,
                orderQuantity=abs(Qty),
                limitPrice=0,
                stopPrice=0,
                orderUniqueIdentifier="454845",
                clientID="PCGDE1569")
              print("RET:",RET)
              if(RET.get('type')=='success'):
                 
                 ret = api.place_order(
                exchangeSegment=api.EXCHANGE_NSEFO,
                exchangeInstrumentID=int(DataStore.get('ShiftToExchangeInstrumentId')),
                productType=api.PRODUCT_NRML,
                orderType=api.ORDER_TYPE_MARKET,
                orderSide=api.TRANSACTION_TYPE_SELL,
                timeInForce=api.VALIDITY_DAY,
                disclosedQuantity=0,
                orderQuantity=abs(Qty),
                limitPrice=0,
                stopPrice=0,
                orderUniqueIdentifier="454845",
                clientID="PCGDE1569")
                 
                  
                 if(ret.get('type') == 'success'):
                  DataStore['QuantityExecuted'] =str(int(float(DataStore['QuantityExecuted'])-Qty))
                  print( DataStore['QuantityExecuted'])
                  DataStore['loop'] = 'False'
                  print("Order Placed")
                  print(ret)
                  Qty = 0
                 else :
                  DataStore['QuantityExecuted'] = DataStore['QuantityExecuted']
                  DataStore['loop'] = 'False'
            #   os.system('cls')
            return DataStore
         else :
              DataStore['QuantityExecuted'] = DataStore['QuantityExecuted']
              DataStore['loop'] = 'False'
              return DataStore
        except Exception as e:
                     
            print(e)
            DataStore['QuantityExecuted'] = DataStore['QuantityExecuted']
            DataStore['loop'] = 'False'
            return DataStore
        
