import requests
import time
import hmac
import hashlib
from urllib.parse import urlencode
import json  # json 모듈 추가

class BingXTrader:
    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = "https://open-api.bingx.com"

    #요청을 위한 사인 제작
    def _sign(self, params):
        query_string = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
        signature = hmac.new(self.secret_key.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
        return signature

    #요청
    def _request(self, method, endpoint, params=None):
        url = f"{self.base_url}{endpoint}"
        headers = {
            'X-BX-APIKEY': self.api_key,
        }

        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status code: {e.response.status_code}")
                print(f"Response content: {e.response.text}")
            return None

    #연결됐다면 프로그램 가능하게
    def test_connection(self):
        try:
            response = self._request('GET', '/openApi/swap/v2/server/time')
            print("API 연결 성공!")
            return True
        except Exception as e:
            print(f"API 연결 실패: {e}")
            return False

    #잔고 요청
    def get_balance(self):
        params = {
            'timestamp': int(time.time() * 1000)
        }
        params['signature'] = self._sign(params)
        response = self._request('GET', '/openApi/swap/v2/user/balance', params)

        if response and 'data' in response and 'balance' in response['data']:
            balance_info = response['data']['balance']
            usdt_balance = float(balance_info.get('balance', 0))
            print(f"현재 USDT 잔고: {usdt_balance} USDT")
            return usdt_balance

        print("USDT 잔고를 찾을 수 없습니다.")
        return 0.0


    #현재 가지고 있는 포지션     전달 파라미터로 온 코인만
    def get_positions(self, symbol):
        params = {
            'symbol': symbol,
            'timestamp': int(time.time() * 1000)
        }
        params['signature'] = self._sign(params)
        response = self._request('GET', '/openApi/swap/v2/user/positions', params)
        print("Positions Response:", response)  # 전체 응답 출력
        positions = response.get('data', [])
        print(f"{symbol} 포지션:")
        for position in positions:
            print(f"수량: {position.get('positionAmt', 'N/A')}, 방향: {position.get('positionSide', 'N/A')}, 레버리지: {position.get('leverage', 'N/A')}")
        return positions


    #숏 포지션 요청
    def open_short_position(self, symbol, amount, price, leverage=10, take_profit_price=None, stop_loss_price=None):
        try:
            # 레버리지 설정
            leverage_params = {
                'symbol': symbol,
                'leverage': int(leverage),
                'side': 'SHORT',
                'timestamp': int(time.time() * 1000)
            }
            leverage_params['signature'] = self._sign(leverage_params)
            leverage_response = self._request('POST', '/openApi/swap/v2/trade/leverage', leverage_params)
            if leverage_response and leverage_response.get('code') != 0:
                print(f"레버리지 설정 실패: {leverage_response.get('msg')}")
                return None

            # Short 포지션 열기 (지정가)
            order_params = {
                'symbol': symbol,
                'side': 'SELL',
                'positionSide': 'SHORT',
                'type': 'LIMIT',
                'price': float(price),
                'quantity': float(amount),
                'timeInForce': 'GTC',
                'timestamp': int(time.time() * 1000)
            }

            # TP와 SL 설정
            if take_profit_price is not None:
                order_params['takeProfit'] = json.dumps({
                    "type": "TAKE_PROFIT_MARKET",
                    "stopPrice": float(take_profit_price)
                })
            if stop_loss_price is not None:
                order_params['stopLoss'] = json.dumps({
                    "type": "STOP_MARKET",
                    "stopPrice": float(stop_loss_price)
                })

            order_params['signature'] = self._sign(order_params)
            response = self._request('POST', '/openApi/swap/v2/trade/order', order_params)
            print(f"Short 포지션 주문 요청: {response}")
            return response
        except Exception as e:
            print(f"Short 포지션 열기 실패: {e}")
            return None


    #스탑로스 요청
    def set_stop_loss(self, symbol, amount, stop_price):
        try:
            params = {
                'symbol': symbol,
                'side': 'BUY',
                'positionSide': 'SHORT',
                'type': 'STOP_MARKET',
                'quantity': amount,
                'stopPrice': stop_price,
                'timestamp': int(time.time() * 1000)
            }
            params['signature'] = self._sign(params)
            response = self._request('POST', '/openApi/swap/v2/trade/order', params)
            print(f"스탑로스 설정: {response}")
            return response
        except Exception as e:
            print(f"스탑로스 설정 실패: {e}")
            return None

    #포지션 종료
    def close_position(self, symbol, amount):
        try:
            params = {
                'symbol': symbol,
                'side': 'BUY',
                'positionSide': 'SHORT',
                'type': 'MARKET',
                'quantity': amount,
                'timestamp': int(time.time() * 1000)
            }
            params['signature'] = self._sign(params)
            response = self._request('POST', '/openApi/swap/v2/trade/order', params)
            print(f"포지션 종료: {response}")
            return response
        except Exception as e:
            print(f"포지션 종료 실패: {e}")
            return None

    #익절 설정
    def set_take_profit(self, symbol, amount, take_profit_price):
        try:
            params = {
                'symbol': symbol,
                'side': 'BUY',
                'positionSide': 'SHORT',
                'type': 'TAKE_PROFIT_MARKET',
                'quantity': amount,
                'stopPrice': take_profit_price,
                'timestamp': int(time.time() * 1000)
            }
            params['signature'] = self._sign(params)
            response = self._request('POST', '/openApi/swap/v2/trade/order', params)
            print(f"익절 설정: {response}")
            return response
        except Exception as e:
            print(f"익절 설정 실패: {e}")
            return None

    def monitor_position(self, symbol, order_amount, entry_price):
        while True:
            positions = self.get_positions(symbol)
            if not positions or all(float(pos.get('positionAmt', 0)) == 0 for pos in positions):
                print("모든 포지션이 종료되었습니다.")
                current_price = self.get_current_price(symbol)
                if current_price:
                    pnl = (entry_price - current_price) * order_amount
                    print(f"최종 손익: {pnl:.2f} USDT")
                break
            time.sleep(5)  # 5초마다 체크

    def get_current_price(self, symbol):
        ticker_params = {
            'symbol': symbol,
            'timestamp': int(time.time() * 1000)
        }
        ticker_params['signature'] = self._sign(ticker_params)
        ticker = self._request('GET', '/openApi/swap/v2/quote/price', ticker_params)

        if ticker and 'data' in ticker and 'price' in ticker['data']:
            return float(ticker['data']['price'])
        else:
            print("현재 가격을 찾을 수 없습니다.")
            return None

    def check_order_status(self, symbol, order_id):
        params = {
            'symbol': symbol,
            'orderId': order_id,
            'timestamp': int(time.time() * 1000)
        }
        params['signature'] = self._sign(params)
        response = self._request('GET', '/openApi/swap/v2/trade/order', params)
        if response and response.get('code') == 0:
            return response['data']['status']
        else:
            return "Unknown"

def run_test():
    api_key = '4s38ctp2pSriQr48PEny2na0Wfs53Xc6dceltgkCrT1Cqc8BaveMtGigFsLZ4674rWJVpxvjbse3gXkl4X3A'
    secret_key = 'j0E1SDqZhTmFwTb5zOkM7Gxdy3oaL72r0Fz9ex7ftqVoK9IRYctXfvGhtZZx7JnueWAjm6e3fs7knk1RbA'
    symbol = 'SOL-USDT'

    trader = BingXTrader(api_key, secret_key)

    if not trader.test_connection():
        return

    balance = trader.get_balance()
    positions = trader.get_positions(symbol)

    # 기존 포지션 확인 및 증거금 사용량 계산
    total_margin_used = 0
    for position in positions:
        position_amt = float(position.get('positionAmt', 0))
        entry_price = float(position.get('entryPrice', 0))
        leverage = float(position.get('leverage', 1))
        position_value = abs(position_amt * entry_price)
        margin_used = position_value / leverage
        total_margin_used += margin_used

    # 증거금 사용량이 전체 잔고의 50% 이상인 경우 경고
    if total_margin_used / balance >= 0.5:
        print(f"경고: 현재 포지션의 증거금 사용량({total_margin_used:.2f} USDT)이 전체 잔고({balance:.2f} USDT)의 50% 이상입니다.")
        print("기존 포지션을 정리하는 것을 고려해 주세요.")
        # 여기서 return을 제거하여 새 포지션 진입을 계속 진행합니다.

    current_price = trader.get_current_price(symbol)
    if current_price is None:
        return

    # 주문 수량 계산 (잔고의 5%를 사용하고 10배 레버리지 적용)
    order_amount = (balance * 0.03 * 10) / current_price
    order_amount = max(1, round(order_amount, 3))  # 최소 1 SOL, 소수점 3자리로 반올림
    leverage = 10

    position_value = order_amount * current_price
    margin_used = position_value / leverage

    print(f"주문 수량: {order_amount} SOL")
    print(f"포지션 가치: {position_value:.2f} USDT")
    print(f"사용될 증거금: {margin_used:.2f} USDT")
    print(f"총 사용 증거금 (기존 + 새 포지션): {total_margin_used + margin_used:.2f} USDT")

    # 지정가 설정 (현재 가격보다 약간 높게)
    limit_price = round(current_price * 1.001, 3)  # 0.1% 높게 설정

    # 손절가 설정 (-1%)
    stop_loss_price = round(current_price * 1.01, 3)

    # 익절가 설정 (0.35%)
    take_profit_price = round(current_price * 0.9965, 3)

    # Short 포지션 열기 (지정가 + TP/SL)
    position = trader.open_short_position(symbol, order_amount, limit_price, leverage, take_profit_price, stop_loss_price)

    if position and position.get('code') == 0:
        print(f"포지션 주문 요청됨: 수량 {order_amount} SOL, 지정가 {limit_price}")
        print(f"손절가: {stop_loss_price} (손실: {(stop_loss_price - limit_price) * order_amount:.2f} USDT)")
        print(f"익절가: {take_profit_price} (이익: {(limit_price - take_profit_price) * order_amount:.2f} USDT)")

        # 주문 상태 확인
        order_id = position['data']['order']['orderId']  # 'orderID'가 아닌 'orderId'
        time.sleep(5)  # 5초 대기
        order_status = trader.check_order_status(symbol, order_id)
        print(f"주문 상태: {order_status}")

        # 포지션 모니터링
        trader.monitor_position(symbol, order_amount, limit_price)
    else:
        print("포지션 주문 요청 실패")

    print("테스트 완료")

if __name__ == "__main__":
    api_key='4s38ctp2pSriQr48PEny2na0Wfs53Xc6dceltgkCrT1Cqc8BaveMtGigFsLZ4674rWJVpxvjbse3gXkl4X3A'
    secret_key='j0E1SDqZhTmFwTb5zOkM7Gxdy3oaL72r0Fz9ex7ftqVoK9IRYctXfvGhtZZx7JnueWAjm6e3fs7knk1RbA'
    bingx_trader = BingXTrader(api_key, secret_key)
    # 현재가 조회 및 출력
    current_price = bingx_trader.get_current_price('BTC-USDT')
    if current_price:
        print(f"\n현재가: {current_price:.2f}")