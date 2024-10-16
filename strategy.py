from strategys.abcstrategy import abcStrategy

class BollingerStrategy:
    def __init__(self):
        self.name = "BollingerStrategy"

    def execute(self, data, indicators, interval):
        data_length = len(data)
        print(f"\n[{interval}]{self.name} 전략 실행 중... 데이터 길이: {data_length}")
        
class WMAStrategy:
    def __init__(self):
        self.name = "WMAStrategy"

    def execute(self, data, indicators, interval):
        data_length = len(data)
        print(f"\n[{interval}]: {self.name} 전략 실행 중... 데이터 길이: {data_length}")




def available_strategies():
    return [BollingerStrategy, WMAStrategy, abcStrategy]


def get_strategy_class(strategyname):
    # 전략 이름에 따라 해당하는 클래스 반환하는 메소드
    strategy_map = {
        "BollingerStrategy": BollingerStrategy,  # 예: 전략1클래스는 실제 전략 클래스 이름으로 교체
        "WMAStrategy": WMAStrategy,
        "abcStrategy": abcStrategy
        # 필요에 따라 더 추가
    }
    return strategy_map.get(strategyname, None)