import sys
import threading
from datetime import datetime
from binance_ws import BinanceWebSocket
from data_manager import DataManager
from rest_api import BinanceAPI
from strategy import available_strategies, get_strategy_class
from input_handler import InputHandler
from chart import plot_candlestick_charts
import time

class MainTrading:

    def __init__(self):
        self.data_manager = DataManager()
        
        self.symbol="btcusdt"
        self.strategies = {
            '1m': [],
            '5m': [],
            '30m': [],
            '1h': []
        }

    #전략추가 mainui와 연동
    def strategyadd(self, timeframe, strategyname):
        strategy_class = get_strategy_class(strategyname)  # strategyname에 해당하는 클래스 가져오기


        if strategy_class is not None and timeframe in self.strategies:
            self.strategies[timeframe].append(strategy_class())
            
            print(f"{strategy_class.__name__} 전략이 {timeframe}에 추가되었습니다.")
                    # 추가된 전략들 실행

    #전략 삭제 main ui와 연동
    def strategydel(self, timeframe, strategyname):
        strategy_class = get_strategy_class(strategyname)  # strategyname에 해당하는 클래스 가져오기

        if strategy_class is not None and timeframe in self.strategies:
            # 인스턴스가 리스트에 존재하는지 확인
            for strategy in self.strategies[timeframe]:
                if isinstance(strategy, strategy_class):
                    self.strategies[timeframe].remove(strategy)
                    print(f"{strategy_class.__name__} 전략이 {timeframe}에 삭제되었습니다.")
                    return  # 한 개만 삭제한 후 종료
            print(f"{strategy_class.__name__} 전략이 {timeframe}에 존재하지 않습니다.")

    #웹소켓 호출시 들어오는 콜백함수
    def data_callback(self,interval, data):

        # 데이터 추가
        self.data_manager.add_data(interval, data)
        self.data_manager.set_indi(interval)
        

        # 추가된 전략들 실행
        for strategy in self.strategies[interval]:

            strategy_data = self.data_manager.get_data(interval)    #데이터 매니저에서 데이터 가져오고
            indicator_data = self.data_manager.get_indi(interval)   #데이터 매니저에서 지표 가져오고
            tfstrategy=strategy.execute(strategy_data, indicator_data, interval)# DataManager의 데이터를 전달
            
            if tfstrategy:
                # 현재 시간 가져오기
                now = datetime.now()

                # 시간 형식을 "MM/DD HH:MM:SS"로 출력
                formatted_time = now.strftime("%m/%d %H:%M:%S")
                print(formatted_time, end='')
                print(tfstrategy)
                #정보 확인 후 매매 하도록 trader에 전달



    def startdata(self):
        """1분봉 5분봉 데이터 restapi, websocket 둘 다 실행"""
        restapi = BinanceAPI()
        
        one_minute_data = restapi.get_klines(self.symbol, "1m")
        self.data_manager.data["1m"]=self.data_manager.convert_api_data(one_minute_data, self.symbol)
        self.data_manager.set_indi('1m')

        five_minute_data = restapi.get_klines(self.symbol, "5m")
        self.data_manager.data["5m"]=self.data_manager.convert_api_data(five_minute_data, self.symbol)
        self.data_manager.set_indi('5m')

        thirty_minute_data = restapi.get_klines(self.symbol, "30m")
        self.data_manager.data["30m"]=self.data_manager.convert_api_data(thirty_minute_data, self.symbol)
        self.data_manager.set_indi('30m')

        one_hour_data = restapi.get_klines(self.symbol, "1h")
        self.data_manager.data["1h"]=self.data_manager.convert_api_data(one_hour_data, self.symbol)
        self.data_manager.set_indi('1h')

        
        ws = BinanceWebSocket(self.symbol, self.data_callback)
        ws_thread = threading.Thread(target=ws.run)
        ws_thread.start()



    def plot_charts(self):
        
        return plot_candlestick_charts(self.data_manager.data['1m'], self.data_manager.data['5m'], self.data_manager.data['30m'],self.data_manager.data['1h'], self.data_manager.indicators)


if __name__ == "__main__":
    main=MainTrading()
