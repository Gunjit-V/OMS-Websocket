import Cred
from Functions import xtsLogin
import time


Credentials = Cred.Puneet


api = xtsLogin(Credentials,'intractive')

# print( api.get_position_netwise().get('result').get('positionList'))
# print(api.get_balance())
start = time.time()

# print(23*2.3)

i = 6
for f in range(i) :
    ret =api.place_order(
        exchangeSegment=api.EXCHANGE_NSEFO,
        exchangeInstrumentID=39067,
        productType=api.PRODUCT_MIS,
        orderType=api.ORDER_TYPE_MARKET,
        orderSide=api.TRANSACTION_TYPE_SELL,
        timeInForce=api.VALIDITY_DAY,
        disclosedQuantity=0,
        orderQuantity=80,
        limitPrice=0,
        stopPrice=0,
        orderUniqueIdentifier="39067",
        clientID="PCGDE1569")
    response = api.get_order_history(appOrderID=ret['result']["AppOrderID"],clientID="PCGDE1569")
    print(response)
    # print(response)

end = time.time()
print(end - start) 
print(ret['result']['AppOrderID'])
# print("Order History: ", response['result'][0]['OrderStatus'])
# Qty =50
# DataStore = {
    
# }
# RET = api.place_order(
#                 exchangeSegment=api.EXCHANGE_NSEFO,
#                 exchangeInstrumentID=DataStore.get('ExchangeInstrumentId'),
#                 productType=api.PRODUCT_MIS,
#                 orderType=api.ORDER_TYPE_MARKET,
#                 orderSide=api.TRANSACTION_TYPE_BUY,
#                 timeInForce=api.VALIDITY_DAY,
#                 disclosedQuantity=0,
#                 orderQuantity=Qty,
#                 limitPrice=0,
#                 stopPrice=0,
#                 orderUniqueIdentifier="454845",
#                 clientID="PCGDE1569")
# print("Ret:",RET)
                
# ret = api.place_order(
#                 exchangeSegment=api.EXCHANGE_NSEFO,
#                 exchangeInstrumentID=DataStore.get('ShiftToExchangeInstrumentId'),
#                 productType=api.PRODUCT_MIS,
#                 orderType=api.ORDER_TYPE_MARKET,
#                 orderSide=api.TRANSACTION_TYPE_SELL,
#                 timeInForce=api.VALIDITY_DAY,
#                 disclosedQuantity=0,
#                 orderQuantity=Qty,
#                 limitPrice=0,
#                 stopPrice=0,
#                 orderUniqueIdentifier="454845",
#                 clientID="PCGDE1569")