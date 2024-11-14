import websocket
import json
import threading
import pandas as pd

class BinanceWebSocket:
    """바이낸스 웹소켓으로 1분봉과 5분봉의 데이터를 받아와서 callback 함수로 쏴준다."""
    def __init__(self, symbols, callback):
        self.symbols = symbols
        self.callback = callback
        self.running = True


    def on_message(self, ws, message):  #웹소켓에서 데이터가 들어올 경우 이리로 옴.
        data = json.loads(message)
        if 'k' in data:  # 캔들 데이터가 포함된 경우
            candle = data['k']
            is_candle_closed = candle['x']
            if is_candle_closed:
                # 1분봉과 5분봉 데이터를 구분하여 콜백 호출
                interval = candle['i']
                self.callback(interval, {
                    'symbol': self.symbols,
                    'open_time': pd.to_datetime(candle['t'], unit='ms'),  # 시작 시간 추가
                    'open': float(candle['o']),
                    'high': float(candle['h']),
                    'low': float(candle['l']),
                    'close': float(candle['c']),
                    'volume': float(candle['v']),
                })

    def on_error(self, ws, error):
        print(f"Error: {error}")

    def on_close(self, ws):
        print("WebSocket closed")
        self.running = False

    def run(self):
        ws = websocket.WebSocketApp(    #1m과 5m이 들어옴.
            f"wss://fstream.binance.com/ws/{self.symbols}@kline_1m/{self.symbols}@kline_5m/{self.symbols}@kline_30m/{self.symbols}@kline_1h",
            # f"wss://stream.binance.com:9443/ws/{self.symbols}@kline_1m/{self.symbols}@kline_5m",
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        ws.run_forever()

    def stop(self):
        self.running = False
