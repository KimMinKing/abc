class StrategyManager:
    def __init__(self):
        # 진입과 청산 조건을 각각 저장할 딕셔너리
        self.entry_conditions = []
        self.exit_conditions = []

    def set_entry_condition(self, condition):
        """진입 조건을 설정하는 메서드"""
        self.entry_conditions.append(condition)

    def set_exit_condition(self, condition):
        """청산 조건을 설정하는 메서드"""
        self.exit_conditions.append(condition)

    def get_entry_conditions(self):
        """진입 조건들을 반환하는 메서드"""
        return self.entry_conditions

    def get_exit_conditions(self):
        """청산 조건들을 반환하는 메서드"""
        return self.exit_conditions



if __name__ == "__main__":
    # test_strategy_manager.py

    # StrategyManager 인스턴스 생성
    strategy_manager = StrategyManager()

    # 진입 조건과 청산 조건을 간단하게 설정 (예: 가격이 특정 값보다 클 때 진입)
    entry_condition = lambda data: data['price'] > 100
    exit_condition = lambda data: data['price'] < 90

    # 진입 조건과 청산 조건 추가
    strategy_manager.set_entry_condition(entry_condition)
    strategy_manager.set_exit_condition(exit_condition)

    # 설정된 진입 조건과 청산 조건 확인
    entry_conditions = strategy_manager.get_entry_conditions()
    exit_conditions = strategy_manager.get_exit_conditions()

    # 테스트 결과 출력
    print("Entry Conditions:", entry_conditions)
    print("Exit Conditions:", exit_conditions)

    # 조건이 올바르게 추가됐는지 확인
    assert len(entry_conditions) == 1, "Entry condition count is incorrect"
    assert len(exit_conditions) == 1, "Exit condition count is incorrect"
    print("StrategyManager 테스트 성공")
