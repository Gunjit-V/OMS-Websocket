from flask import Flask, jsonify, send_from_directory
from Functions import xtsLogin , FindDiffBtwTwoStrikes , FetchPositions,GetAllStrikeData,CheckAndTrade
from flask_socketio import SocketIO, send, emit
import Cred
from flask import copy_current_request_context
import csv
import traceback


import MarketdataSocketExample
from MarketDataSocketClient import MDSocket_io
from Connect import XTSConnect
import os 
import time
import json
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins='*')
global DataStore
global Instruments
global FetchedData 
global emiting 
Credentials  = Cred.Puneet

api = xtsLogin(Credentials,'intractive')
# api2 = xtsLogin(Credentials, 'marketfeed')

def save_print_to_csv(message, function_name, line_number):
    with open('print_log.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([message, function_name, line_number])


# def save_print_to_csv(message, function_name, line_number):
#     with open('print_log.csv', mode='a', newline='') as file:
#         writer = csv.writer(file)
#         writer.writerow([message, function_name, line_number])


@socketio.on('FindDifferenceBtwTwoStrikes')
def Diff(Token1 , Token2):
    try:
        Difference = FindDiffBtwTwoStrikes(api2 ,Token2 , Token1)
        print(Difference)
        emit('DiffernceResponse', Difference)
    except Exception as e:
        print(e)

   
@socketio.on('FetchPositions')
def Diff(data):
    try:
        print("IN")
        Positions = FetchPositions(api)
        emit('FetchPositionsResponse', Positions)
    except Exception as e:
        print(e)

    
@socketio.on('GetAllStrikeData')
def getStrikes(symbols):
    try:
        print("IN")
        Strikes = GetAllStrikeData(api2, symbols)
        emit('GetAllStrikeDataResponse', Strikes)
    except Exception as e:
        print(e)
    
@socketio.on('Scanning')
def Scanning(DataArray):
    try:
        global Instruments
        global DataStore
        DataStore = DataArray
        print("IN")
        NewInstruments =[]
        for i in DataArray:
            NewInstruments.append({'exchangeSegment': 2, 'exchangeInstrumentID': int(i['ExchangeInstrumentId'])})
            NewInstruments.append({'exchangeSegment': 2, 'exchangeInstrumentID': int(i['ShiftToExchangeInstrumentId'])})
        if len(NewInstruments ) ==0:
            NewInstruments.append({'exchangeSegment': 1, 'exchangeInstrumentID': 26000})
        api2.send_unsubscription(Instruments , 1501)
        api2.send_subscription(NewInstruments, 1501)
        Instruments = NewInstruments
        # os.system('cls')
        emit('ScanningResponse', DataArray, broadcast=True)
    except Exception as e:
        print(e)
    


@socketio.on('connect')
def test_connect():
    print('CONNECT EVENT happened...')
    emit('Success', "Connected")

@socketio.on('Notification')
def notify(message):
    try:
        # os.system('cls')
        print('Notification Recieved: ' ,message)
        time.sleep(5)
        DataStore[0]['QuantityExecuted'] =str( int(DataStore[0]['QuantityExecuted']) + 100)
        emit("ScanningResponse", DataStore)
        emit('NotificationResponse', "100 Qty 19800 Punched")
    except Exception as e:
        print(e)



if __name__ == '__main__':
    try:
        DataStore = []
        FetchedData ={}
        Instruments =[{'exchangeSegment': 1, 'exchangeInstrumentID': 26000}]
        api2 = XTSConnect(Credentials["API_KEY_marketfeed"], Credentials['API_SECRET_marketfeed'], "WEBAPI")
        response = api2.marketdata_login()
        print(response)
        # Store the token and userid
        set_marketDataToken = response['result']['token']
        set_muserID = response['result']['userID']
        print("Login: ", response)

        # Connecting to Marketdata socket
        soc = MDSocket_io(set_marketDataToken, set_muserID)

        # Callback for connection
        def on_connect():
            """Connect from the socket."""
            print('Market Data Socket connected successfully!')

            # # Subscribe to instruments
            print('Sending subscription request for Instruments - \n' + str(Instruments))
            response = api2.send_subscription(Instruments, 1501)
            print('Sent Subscription request!')
            print("Subscription response: ", response)
        
        # Callback on receiving message
        def on_message(data):
            print('I received a message!')

        # Callback for message code 1501 FULL
        def on_message1501_json_full(data):
            # print(Instruments)
            global DataStore
            global FetchedData 
            data = json.loads(data)
           
            FetchedData[data.get("ExchangeInstrumentID")] =data
            
            out_file = open("myfile.json", "w")
      
            json.dump(FetchedData, out_file, indent = 6)
            out_file.close()
            
            
            for i in DataStore:
                if( i.get('QuantityExecuted') !=str(i.get('QuantityToBeExecuted'))):
                    Qty = int(i.get('QuantityToBeExecuted') -int(i.get('QuantityExecuted')))
                    i['QuantityExecuted'] =str(i.get('QuantityToBeExecuted'))
                    i = CheckAndTrade(api , i ,FetchedData  , Qty )
                    print("FinalDataStore: ", i)
                    if( i.get('QuantityExecuted') ==str(i.get('QuantityToBeExecuted'))):
                         with app.test_request_context('/'):
                             socketio.emit('ScanningResponse', DataStore, broadcast=True)
                    
                    
                

            # os.system('cls')    
            # print(DataStore)
            # print('I received a 1501 Touchline message!' + data)

        # Callback for message code 1502 FULL
        def on_message1502_json_full(data):
            print('I received a 1502 Market depth message!' + data)

        # Callback for message code 1505 FULL
        def on_message1505_json_full(data):
            print('I received a 1505 Candle data message!' + data)

        # Callback for message code 1507 FULL
        def on_message1507_json_full(data):
            print('I received a 1507 MarketStatus data message!' + data)

        # Callback for message code 1510 FULL
        def on_message1510_json_full(data):
            print('I received a 1510 Open interest message!' + data)

        # Callback for message code 1512 FULL
        def on_message1512_json_full(data):
            print('I received a 1512 Level1,LTP message!' + data)

        # Callback for message code 1505 FULL
        def on_message1505_json_full(data):
            print('I received a 1505, Instrument Property Change Event message!' + data)


        # Callback for message code 1501 PARTIAL
        def on_message1501_json_partial(data):
            print("Partial")
            # print('I received a 1501, Touchline Event message!' + data)

        # Callback for message code 1502 PARTIAL
        def on_message1502_json_partial(data):
            print('I received a 1502 Market depth message!' + data)

        # Callback for message code 1505 PARTIAL
        def on_message1505_json_partial(data):
            print('I received a 1505 Candle data message!' + data)

        # Callback for message code 1510 PARTIAL
        def on_message1510_json_partial(data):
            print('I received a 1510 Open interest message!' + data)

        # Callback for message code 1512 PARTIAL
        def on_message1512_json_partial(data):
            print('I received a 1512, LTP Event message!' + data)



        # Callback for message code 1505 PARTIAL
        def on_message1505_json_partial(data):
            print('I received a 1505, Instrument Property Change Event message!' + data)

        # Callback for disconnection
        def on_disconnect():
            print('Market Data Socket disconnected!')


        # Callback for error
        def on_error(data):
            """Error from the socket."""
            print('Market Data Error', data)


        # Assign the callbacks.
        soc.on_connect = on_connect
        soc.on_message = on_message
        soc.on_disconnect = on_disconnect
        soc.on_error = on_error


        # Event listener
        el = soc.get_emitter()
        el.on('connect', on_connect)
        el.on('1501-json-full', on_message1501_json_full)
        # el.on('1502-json-full', on_message1502_json_full)
        # el.on('1507-json-full', on_message1507_json_full)
        # el.on('1512-json-full', on_message1512_json_full)
        # el.on('1505-json-full', on_message1505_json_full)

        # Infinite loop on the main thread. Nothing after this will run.
        # You have to use the pre-defined callbacks to manage subscriptions.
        soc.connect()
        emiting = emit

        socketio.run(app)




        @ socketio.on('disconnect', namespace='/test')
        def test_disconnect():
            print('Client disconnected')
    except Exception as e:
        print('An error occurred:', e)
