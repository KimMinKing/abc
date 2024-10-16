import pandas as pd

class abcStrategy:
    def __init__(self, is_live=True, balance=100000):
        self.name = "ABCStrategy"
        self.entry_price = None
        self.position = None
        self.balance = balance
        self.is_live=is_live    #초기값 false
        # 전역 설정
        self.settings = {
            'capital_percentage': 1.0,  # 총 자본 중 사용할 비율 (%)
            'leverage': 50,  # 레버리지
            'stop_loss_percentage': 1.0,  # 손실 제한 비율 (%)
            'take_profit_percentage': 0.33,  # 이익 실현 비율 (%)
            'max_open_positions': 2,  # 최대 동시 오픈 포지션 수
            'trading_enabled': True,  # 거래 활성화 여부
        }

    def entry_signal(self, data, indicators, interval):
        # 인디케이터 조합으로 진입 신호 계산

        condition_1 =indicators['below_wmas']
        # abc가 10개봉 전까지 True였던 부분 찾기
        condition_2 = indicators['abcstrategy'].rolling(window=10).max().shift() > 0
        combined_condition = condition_1 & condition_2

        if self.is_live:
            return combined_condition.iloc[-1]  # 실시간 거래: 마지막 값
        else:
            return combined_condition  # 백테스팅: 전체 Series 반환

    def exit_signal(self, data, indicators):
        # 청산 신호 계산 (진입 조건의 반대나 손익 계산 등)
        pass

    def execute(self, data, indicators, interval):
        """스트레터지의 메인임."""

        if self.position is None:  # 포지션이 없을 때

            if self.entry_signal(data, indicators, interval):   #진입조건 검사 후 가져오기

                return self.enter_position(data, indicators, interval)    #익절가 손절가 전략에 맞게 꼐산 후 리턴

        else:                       # 포지션이 있을 때

            if self.exit_signal(data, indicators, interval):    #종료조건 검사 후 가져오기

                self.exit_position(data)

    def enter_position(self, data, indicators, interval):
        print("enter_position")
        # 포지션 진입 로직
        self.position = True
        self.entry_price, current_price = data['close'].tail(1).values[0]

        #얼마나 매입할건지
        capital_to_use = self.balance * (self.settings['capital_percentage'] / 100) 
        order_amount = (capital_to_use * self.settings['leverage']) / self.entry_price

        #손절가
        recent_true_index = indicators[interval]['abcstrategy'][::-1].idxmax()  #시그널의 고가
        data.set_index('time', inplace=True)        #인덱스를 time으로

        stop_loss_price =data.loc[recent_true_index]['high']      #최고가를 손절가로 하고 변수화
        # 현재가와 최고가의 차이를 퍼센트로 계산
        percentage_difference = ((stop_loss_price - current_price) / stop_loss_price) * 100

        # 익절가는 현재가에서 (퍼센트 차이의 2/3)을 뺀 값
        take_profit_price = current_price - (percentage_difference * 2 / 3 / 100 * stop_loss_price)

        # 결과 출력
        print(f"손절가 {stop_loss_price:.2f}원 ({percentage_difference:.2f}%)")
        print(f"익절가 {take_profit_price:.2f}원 ({-percentage_difference * 2 / 3:.2f}%)")


        order={
            "심볼":"BTC-USDT",
            "주문 유형":"Short",
            "수량":order_amount,
            "진입가":self.entry_price,
            "손절가":stop_loss_price,
            "익절가":take_profit_price
        }
        
        print(f"{self.name} - 진입 {self.entry_price}")
        return order

    def exit_position(self, data):
        # 포지션 청산 로직
        self.position = None
        self.entry_price = None


    def calculate_order_amount(self, data):
        # 진입 가격과 현재 가격 가져오기
        self.entry_price, current_price = data['close'].tail(1).values[0]

        # 손절가 퍼센트 계산
        stop_loss_percentage = (self.entry_price - self.stop_loss_price) / self.entry_price * 100

        # 자본의 일정 비율 사용
        capital_to_use = self.balance * (self.settings['capital_percentage'] / 100)

        # 손절가 퍼센트가 1% 이상일 경우, capital_to_use를 절반으로 줄임
        if stop_loss_percentage > 1:
            capital_to_use /= 2

        # 주문 수량 계산
        order_amount = (capital_to_use * self.settings['leverage']) / self.entry_price

        return order_amount
