import pandas as pd
from collections import deque
from indicator import Indicator
from datetime import datetime

class DataManager:
    def __init__(self, max_size=1000):
        self.data = {
            '1m': deque(maxlen=max_size),
            '5m': deque(maxlen=max_size),
            '1h': deque(maxlen=max_size)
        }

        self.indicators={
            '1m':{
            'fs': None,
            'fs2': None,
            'fs3': None,
            'ultimate': None,
            'percenthl': None,
            'smi': None,
            'wma12': None
            },
            '5m':{
            'fs': None,
            'fs2': None,
            'fs3': None,
            'ultimate': None,
            'percenthl': None,
            'smi': None,
            'wma12': None
            }

        }
    
        self.indicator=Indicator()

    def set_indi(self, interval):

        self.indicators[interval]=self.indicator.setindicators(self.indicators[interval], self.data[interval])



    def add_data(self, interval, new_data):
        """주어진 시간봉에 새로운 가격 정보를 추가합니다."""
        if interval in self.data:
            # new_data['time'] = new_data['time'].strftime('%Y-%m-%d %H:%M:%S')
            # print(f"\n{new_data['time']} type = {type(new_data['time'])}")
            # print(f"{self.data['1m']['time'].tail(1)} type = {type(self.data['1m']['time'].tail(1))}")
            # new_data를 DataFrame 형식으로 변환
            new_entry = pd.DataFrame([{
                "symbol": new_data["symbol"],
                "time": pd.to_datetime(new_data["open_time"]),  # 이미 변환된 Timestamp 형식
                "open": new_data["open"],
                "high": new_data["high"],
                "low": new_data["low"],
                "close": new_data["close"],
                "volume": new_data["volume"]
            }])

            # 기존 데이터와 새로운 데이터를 결합
            combined_df = pd.concat([self.data[interval], new_entry], ignore_index=True)

            # time을 기준으로 중복된 행을 제거 (나중에 들어온 데이터 우선)
            combined_df.drop_duplicates(subset=['time'], keep='last', inplace=True)

            # 중복 제거 후의 결과를 self.data[interval]에 저장
            self.data[interval] = combined_df.reset_index(drop=True)

            # 데이터 개수가 1000개를 초과하면 오래된 데이터를 제거
            if len(self.data[interval]) > 1000:
                self.data[interval] = self.data[interval].iloc[1:].reset_index(drop=True)
        else:
            # interval이 존재하지 않는 경우 초기화
            self.data[interval] = pd.DataFrame([new_data])



    
    def get_data(self, interval):
        """주어진 시간봉의 DataFrame을 반환합니다."""
        return self.data[interval]
    def get_indi(self, interval):
        """주어진 시간봉의 DataFrame을 반환합니다."""
        return self.indicators[interval]


    def get_latest(self, interval, n=10):
        """주어진 시간봉의 가장 최근 n개의 데이터를 반환합니다."""
        return self.data[interval].tail(n)

    def clear_data(self, interval):
        """주어진 시간봉의 데이터를 초기화합니다."""
        if interval in self.data:
            self.data[interval].clear()



    def convert_api_data(self, api_data, symbol):
        """
        API에서 받아온 데이터를 원하는 형식으 로 변환합니다.
        
        :param api_data: REST API로부터 받은 원본 데이터
        :param symbol: 거래 심볼 (예: 'btcusdt')
        :return: 변환된 데이터프레임
        """
        formatted_data = []

        for entry in api_data:
            formatted_entry = {
                "symbol": symbol,
                "time": pd.to_datetime(entry[0], unit='ms'),  # 시작 시간 변환
                "open": float(entry[1]),
                "high": float(entry[2]),
                "low": float(entry[3]),
                "close": float(entry[4]),
                "volume": float(entry[5]),
            }
            formatted_data.append(formatted_entry)

        # 데이터프레임으로 변환
        return pd.DataFrame(formatted_data)
    