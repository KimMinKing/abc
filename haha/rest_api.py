import requests

class BinanceAPI:
    BASE_URL = "https://fapi.binance.com/fapi/v1/klines"

    @staticmethod
    def get_klines(symbol, interval, limit=1000):
        """주어진 심볼, 시간봉, 개수에 대한 Kline 데이터를 가져옵니다."""
        params = {
            'symbol': symbol.upper(),
            'interval': interval,
            'limit': limit
        }
        response = requests.get(BinanceAPI.BASE_URL, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error fetching data: {response.status_code} - {response.text}")



# 사용 예시
if __name__ == "__main__":
    api = BinanceAPI()
    try:
        one_minute_data = api.get_klines("btcusdt", "1m")
        five_minute_data = api.get_klines("btcusdt", "5m")
        one_hour_data = api.get_klines("btcusdt", "1h")
        
        print(f"1분봉 데이터 수: { (one_minute_data)}")

        
    except Exception as e:
        print(e)
