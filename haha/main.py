import sys
import threading
from binance_ws import BinanceWebSocket
from data_manager import DataManager
from rest_api import BinanceAPI
from strategy import available_strategies
from input_handler import show_main_menu, show_strategy_menu, show_remove_menu, show_check_strategies


class MainTrading:

    def main(self):
        self.data_manager = DataManager()
        
        self.symbol="btcusdt"
        self.strategies = {
            '1m': [],
            '5m': [],
            '1h': []
        }

        def data_callback(interval, data):
            # 데이터 추가

            self.data_manager.add_data(interval, data)

            self.data_manager.set_indi(interval)

            
            # 추가된 데이터 출력 (예시)
            # print(f"--- {self.data_manager.get_latest(interval, 5)}")  # 해당 시간봉의 최근 5개 데이터 출력

            # 기존 전략 실행
            for strategy in self.strategies[interval]:
                strategy_data = self.data_manager.get_data(interval)

                indicator_data = self.data_manager.get_indi(interval)

                strategy.execute(strategy_data, indicator_data, interval)  # DataManager의 데이터를 전달


        def startdata():
            """1분봉 5분봉 데이터 restapi, websocket 둘 다 실행"""
            restapi = BinanceAPI()
            one_minute_data = restapi.get_klines(self.symbol, "1m")
            self.data_manager.data["1m"]=self.data_manager.convert_api_data(one_minute_data, self.symbol)
            five_minute_data = restapi.get_klines(self.symbol, "5m")
            self.data_manager.data["5m"]=self.data_manager.convert_api_data(five_minute_data, self.symbol)

            
            ws = BinanceWebSocket(self.symbol, data_callback)
            ws_thread = threading.Thread(target=ws.run)
            ws_thread.start()


        startdata()


        try:
            while True:
                choice = show_main_menu()
                if choice == '1':  # 전략 추가
                    available = show_strategy_menu()
                    strategy_choice = input("추가할 전략의 번호를 선택하세요: ")
                    try:
                        index = int(strategy_choice) - 1
                        if 0 <= index < len(available):
                            strategy_class = available[index]
                            timeframe = input("어떤 시간봉의 전략을 추가하시겠습니까? (1m, 5m, 1h): ")
                            if timeframe in self.strategies:
                                # 중복 체크
                                if any(isinstance(strategy, strategy_class) for strategy in self.strategies[timeframe]):
                                    print(f"{strategy_class.__name__} 전략은 이미 {timeframe}에 추가되어 있습니다.")
                                else:
                                    self.strategies[timeframe].append(strategy_class())
                                    print(f"{strategy_class.__name__} 전략이 {timeframe}에 추가되었습니다.")
                            else:
                                print("잘못된 시간봉입니다.")
                        else:
                            print("잘못된 번호입니다.")
                    except ValueError:
                        print("숫자를 입력하세요.")
                elif choice == '2':  # 전략 제거
                    timeframe = input("어떤 시간봉의 전략을 제거하시겠습니까? (1m, 5m, 1h): ")
                    if timeframe in self.strategies and self.strategies[timeframe]:
                        remove_choice = show_remove_menu(self.strategies[timeframe])
                        try:
                            index = int(remove_choice) - 1
                            if 0 <= index < len(self.strategies[timeframe]):
                                removed_strategy = self.strategies[timeframe].pop(index)
                                print(f"{removed_strategy.name} 전략이 제거되었습니다.")
                            else:
                                print("잘못된 번호입니다.")
                        except ValueError:
                            print("숫자를 입력하세요.")
                    else:
                        print("해당 시간봉에 추가된 전략이 없습니다.")
                elif choice == '3':  # 프로그램 종료
                    break
                elif choice == '4':  # 전략 확인
                    show_check_strategies(self.strategies)
                else:
                    print("잘못된 선택입니다.")

        except KeyboardInterrupt:
            print("\n프로그램이 강제 종료되었습니다.")
            sys.exit(0)  # 강제 종료



if __name__ == "__main__":
    main=MainTrading()
    main.main()
