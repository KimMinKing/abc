class Trader:
    def __init__(self, initial_balance):
        self.balance = initial_balance
        self.position = None
        self.entry_price = None
        self.entry_quantity = None  # 수량 추가
        self.stop_loss = None
        self.take_profit = None
        self.fee_rate = 0.05  # 수수료율 0.05 적용
        self.logs = []

    def enter_position(self, price, quantity, position_type, stop_loss=None, take_profit=None):
        total_value = price * quantity
        if total_value > self.balance:
            print("잔액이 부족하여 포지션에 진입할 수 없습니다.")
            return

        if self.position is None:
            self.position = position_type
            self.entry_price = price
            self.entry_quantity = quantity  # 수량 저장
            self.stop_loss = stop_loss
            self.take_profit = take_profit
            self.balance -= total_value  # 포지션 진입 시 잔액 감소
            self.logs.append(f"{price} 가격에 {quantity}개의 {position_type} 진입")
            print(f"{price} 가격에 {quantity}개의 {position_type} 진입")
        else:
            print("이미 포지션이 존재하여 새로운 포지션을 진입할 수 없습니다.")

    def exit_position(self, price):
        if self.position is not None:
            profit = self.calculate_profit(price)
            self.balance += profit  # 청산 후 잔액 증가
            self.logs.append(f"{price} 가격에 {self.position} 청산, 수익: {profit}")
            print(f"{price} 가격에 {self.position} 청산, 수익: {profit}")
            self.position = None
            self.entry_price = None
            self.entry_quantity = None  # 수량 초기화
            self.stop_loss = None
            self.take_profit = None
        else:
            print("청산할 포지션이 없습니다.")

    def calculate_profit(self, exit_price):
        if self.position == 'short':
            raw_profit = (self.entry_price - exit_price) * self.entry_quantity
            fee = abs(raw_profit) * self.fee_rate
            return raw_profit - fee
        return 0

    def check_stop_loss(self, current_price):
        if self.stop_loss and self.position == 'short' and current_price >= self.stop_loss:
            self.exit_position(current_price)
            print(f"스톱로스 {current_price}에 도달하여 포지션 청산")

    def check_take_profit(self, current_price):
        if self.take_profit and self.position == 'short' and current_price <= self.take_profit:
            self.exit_position(current_price)
            print(f"익절 {current_price}에 도달하여 포지션 청산")

    def check_balance(self):
        print(f"현재 잔고: {self.balance}")
        return self.balance

    def cancel_order(self):
        if self.position is not None:
            print(f"{self.position} 포지션 주문이 취소되었습니다.")
            self.position = None
            self.entry_price = None
        else:
            print("취소할 주문이 없습니다.")

    # 손절 메서드
    def set_stop_loss(self, stop_loss):
        self.stop_loss = stop_loss
        print(f"손절가가 {stop_loss}로 설정되었습니다.")

    # 익절 메서드
    def set_take_profit(self, take_profit):
        self.take_profit = take_profit
        print(f"익절가가 {take_profit}로 설정되었습니다.")



# main 함수
def main():
    # 트레이더 초기화 (초기 자본금 10,000)
    trader = Trader(initial_balance=10000)
    
    # 1. 포지션 진입 테스트 (수량 포함)
    print("=== Entering Position ===")
    trader.enter_position(price=63000, quantity=0.1, position_type='short', stop_loss=63500, take_profit=62000)
    trader.check_balance()
    
    # 2. 손절 체크 테스트 (현재 가격이 손절가에 도달했을 때)
    print("=== Checking Stop Loss ===")
    trader.check_stop_loss(current_price=63500)  # 손절가를 트리거
    trader.check_balance()
    
    # 3. 포지션 진입 후 익절 테스트
    print("=== Entering Position Again ===")
    trader.enter_position(price=64000, quantity=0.2, position_type='short', stop_loss=64500, take_profit=63000)
    trader.check_balance()
    
    print("=== Checking Take Profit ===")
    trader.check_take_profit(current_price=63000)  # 익절가를 트리거
    trader.check_balance()

    # 4. 포지션 청산 테스트
    print("=== Exiting Position ===")
    trader.enter_position(price=64000, quantity=0.1, position_type='short', stop_loss=64500, take_profit=63000)
    trader.exit_position(price=63000)
    trader.check_balance()

    # 5. 잔고 확인 테스트
    print("=== Checking Balance ===")
    trader.check_balance()
    
    # 6. 주문 취소 테스트
    print("=== Canceling Order ===")
    trader.enter_position(price=64000, quantity=0.2, position_type='short', stop_loss=64500, take_profit=63000)
    trader.cancel_order()
    trader.check_balance()
    
    # 7. 로그 출력
    print("=== Trade Logs ===")
    for log in trader.logs:
        print(log)

# 메인 함수 실행
if __name__ == "__main__":
    main()