from strategy import available_strategies


class InputHandler:
        
    def show_main_menu(self):
        print("\n메인 메뉴:")
        print("1. 전략 추가")
        print("2. 전략 제거")
        print("3. 프로그램 종료")
        print("4. 전략 확인")
        return input("옵션을 선택하세요: ")

    def show_strategy_menu(self):
        print("\n사용 가능한 전략:")
        strategies = available_strategies()
        for idx, strategy in enumerate(strategies, start=1):
            print(f"{idx}. {strategy.__name__}")
        return strategies

    def show_remove_menu(self,strategies):
        print("\n제거할 전략 선택:")
        for idx, strategy in enumerate(strategies, start=1):
            print(f"{idx}. {strategy.name}")
        return input("제거할 전략의 번호를 입력하세요: ")

    def show_check_strategies(self,strategies):
        print("\n현재 추가된 전략 목록:")
        for timeframe, strategy_list in strategies.items():
            print(f"{timeframe}: {[strategy.__class__.__name__ for strategy in strategy_list] if strategy_list else '없음'}")


