import requests
import json
import threading
import time
from requests.exceptions import ConnectionError, Timeout, RequestException

class TelegramBot:
    def __init__(self, token, chat_id, captials=1000000):
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{self.token}/"
        self.last_update_id = 0
        self.message_handlers = {}
        self.listening = False
        self.current_menu = "main"
        self.waiting_for_input = False
        self.capital = captials  # 초기 자본금
        self.chart_request_callback = None  # 차트 요청 콜백 함수
        self.trading_active = True  # 거래 활성화 상태를 나타내는 변수


    def handle_start_trade(self):
        if not self.trading_active:
            self.trading_active = True
            self._send_text("거래가 시작되었습니다.")
            # self.show_trading_options()
        else:
            self._send_text("이미 거래가 활성화된 상태입니다.")


    def handle_stop_trade(self):
        if self.trading_active:
            self.trading_active = False
            self._send_text("거래가 중지되었습니다.")
            print("거래가 중지되었습니다.")  # 콘솔에 출력
            self.show_pause_options()
        else:
            self._send_text("이미 거래가 중지된 상태입니다.")
            print("이미 거래가 중지된 상태입니다.")  # 콘솔에 출력


    def show_pause_options(self):
        keyboard = {
            'inline_keyboard': [
                [{'text': '15분', 'callback_data': 'pause_15'},
                 {'text': '30분', 'callback_data': 'pause_30'},
                 {'text': '1시간', 'callback_data': 'pause_60'}],
                [{'text': '수동으로 재개', 'callback_data': 'manual_resume'}]
            ]
        }
        self._send_text("얼마 후 거래를 재개할까요?", reply_markup=json.dumps(keyboard))

    def handle_pause(self, duration):
        if duration == 'manual':
            self._send_text("거래가 수동으로 재개될 때까지 중지됩니다. 재개하려면 '3. 거래 시작' 메뉴를 선택하세요.")
            print("거래가 수동으로 중지되었습니다.")  # 콘솔에 출력
        else:
            minutes = int(duration)
            self._send_text(f"{minutes}분 후에 거래가 자동으로 재개됩니다.")
            print(f"거래가 {minutes}분 동안 중지되었습니다.")  # 콘솔에 출력
            threading.Timer(minutes * 60, self.resume_trade).start()
        self.trading_active = False  # 거래 상태를 비활성화로 설정

    def resume_trade(self):
        if not self.trading_active:
            self.trading_active = True
            self._send_text("거래가 재개되었습니다.")
            print("거래가 재개되었습니다.")  # 콘솔에 출력
        else:
            self._send_text("이미 거래가 활성화된 상태입니다.")
            print("이미 거래가 활성화된 상태입니다.")  # 콘솔에 출력


    def send_message(self, message, chart_path=None, btn=False):
        try:
            if chart_path:
                return self._send_photo(message, chart_path, btn)
            else:
                return self._send_text(message, btn)
        except Exception as e:
            print(f"텔레그램 메시지 전송 실패: {e}")

    def _send_text(self, message, btn=False, reply_markup=None):
        url = self.base_url + "sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        if btn:
            keyboard = {
                'inline_keyboard': [[
                    {'text': '거래 진행', 'callback_data': 'proceed'},
                    {'text': '거래 패스', 'callback_data': 'pass'}
                ]]
            }
            payload['reply_markup'] = json.dumps(keyboard)
        elif reply_markup:
            payload['reply_markup'] = reply_markup
        response = requests.post(url, json=payload)
        return response.json()

    def _send_photo(self, caption, photo_path, btn=False):
        url = self.base_url + "sendPhoto"
        payload = {
            "chat_id": self.chat_id,
            "caption": caption,
            "parse_mode": "HTML"
        }
        if btn:
            keyboard = {
                'inline_keyboard': [[
                    {'text': '거래 진행', 'callback_data': 'proceed'},
                    {'text': '거래 패스', 'callback_data': 'pass'}
                ]]
            }
            payload['reply_markup'] = json.dumps(keyboard)
        with open(photo_path, 'rb') as photo:
            files = {'photo': photo}
            response = requests.post(url, data=payload, files=files)
        return response.json()

    def set_main_menu(self):
        keyboard = {
            'keyboard': [
                ['1. 거래 수정'],
                ['2. 거래 중지'],
                ['3. 거래 시작'],
                ['4. 차트 요청']
            ],
            'resize_keyboard': True,
            'one_time_keyboard': False
        }
        self._send_menu("메인 메뉴입니다. 원하는 옵션을 선택하세요.", keyboard)
        self.current_menu = "main"

    def set_sub_menu(self):
        keyboard = {
            'keyboard': [
                ['1-1. 전략 수정'],
                ['1-2. 금액 수정'],
                ['1-3. 시간 수정'],
                ['뒤로 가기']
            ],
            'resize_keyboard': True,
            'one_time_keyboard': False
        }
        self._send_menu("거래 수정 메뉴입니다. 원하는 옵션을 선택하세요.", keyboard)
        self.current_menu = "sub"

    def set_main_menu(self):
        keyboard = {
            'keyboard': [
                ['1. 거래 수정'],
                ['2. 거래 중지'],
                ['3. 거래 시작'],
                ['4. 차트 요청']
            ],
            'resize_keyboard': True,
            'one_time_keyboard': False
        }
        self._send_menu("메인 메뉴입니다. 원하는 옵션을 선택하세요.", keyboard)
        self.current_menu = "main"

    def set_sub_menu(self):
        keyboard = {
            'keyboard': [
                ['1-1. 전략 수정'],
                ['1-2. 금액 수정'],
                ['1-3. 시간 수정'],
                ['뒤로 가기']
            ],
            'resize_keyboard': True,
            'one_time_keyboard': False
        }
        self._send_menu("거래 수정 메뉴입니다. 원하는 옵션을 선택하세요.", keyboard)
        self.current_menu = "sub"

    def set_strategy_menu(self):
        keyboard = {
            'keyboard': [
                ['Sky Blue'],
                ['Dark Blue'],
                ['All Blue'],
                ['뒤로 가기']
            ],
            'resize_keyboard': True,
            'one_time_keyboard': False
        }
        self._send_menu("전략을 선택하세요.", keyboard)
        self.current_menu = "strategy"

    def _send_menu(self, text, keyboard):
        url = self.base_url + "sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "reply_markup": json.dumps(keyboard)
        }
        response = requests.post(url, json=payload)
        return response.json()


    def get_updates(self, offset=None):
        url = self.base_url + "getUpdates"
        params = {"timeout": 100, "offset": offset}
        try:

            response = requests.get(url, params=params)
            response.raise_for_status()  # HTTP 오류 발생 시 예외 처리
        except ConnectionError:
            print("Error: Failed to connect to the server.")
        except Timeout:
            print("Error: The request timed out.")
        except RequestException as e:
            print(f"An error occurred: {e}")


        return response.json()

    def start_listening(self):
        self.listening = True
        threading.Thread(target=self._listen, daemon=True).start()

    def _listen(self):
        while self.listening:
            updates = self.get_updates(self.last_update_id + 1)
            if "result" in updates:
                for update in updates["result"]:
                    self.last_update_id = update["update_id"]
                    if "message" in update and "text" in update["message"]:
                        message_text = update["message"]["text"]
                        print(f"받은 메시지: {message_text}")
                        self._handle_message(message_text)
                    elif "callback_query" in update:
                        callback_query = update["callback_query"]
                        self._handle_callback_query(callback_query)
            time.sleep(1)



    def send_chart(self, chart_data):
        url = self.base_url + "sendPhoto"
        files = {'photo': ('chart.png', chart_data, 'image/png')}
        data = {'chat_id': self.chat_id}
        response = requests.post(url, files=files, data=data)

        if response.status_code == 200:
            print("차트가 성공적으로 전송되었습니다.")
        else:
            print("차트 전송에 실패했습니다.")

    def set_chart_request_callback(self, callback):
        self.chart_request_callback = callback


    def _handle_callback_query(self, callback_query):
        callback_data = callback_query["data"]

        if callback_data.startswith("pause_"):
            duration = callback_data.split("_")[1]
            self.handle_pause(duration)
        elif callback_data == "manual_resume":
            self.handle_pause('manual')
        elif callback_data == "proceed":
            new_text = "거래 진행을 선택하셨습니다."
        elif callback_data == "pass":
            new_text = "거래 패스를 선택하셨습니다."
        else:
            new_text = "알 수 없는 선택입니다."

        if not callback_data.startswith("pause_") and not callback_data == "manual_resume":
            self._send_text(new_text)

        self.answer_callback_query(callback_query["id"])

        if callback_data in self.message_handlers:
            self.message_handlers[callback_data]()

    def _handle_message(self, message_text):
        if self.waiting_for_input:
            try:
                new_capital = int(message_text)
                self.capital = new_capital
                self._send_text(f"자본금이 {new_capital}원으로 설정되었습니다.")
                self.waiting_for_input = False
                self.set_sub_menu()
            except ValueError:
                self._send_text("올바른 숫자를 입력해주세요.")
            return

        if self.current_menu == "main":
            if message_text == "1. 거래 수정":
                self.set_sub_menu()
            elif message_text == "2. 거래 중지":
                self.show_pause_options()
            elif message_text == "3. 거래 시작":
                self.resume_trade()
            elif message_text == "4. 차트 요청":
                if self.chart_request_callback:
                    self.chart_request_callback()
                else:
                    self._send_text("차트 요청 기능이 설정되지 않았습니다.")
            elif message_text in self.message_handlers:
                self.message_handlers[message_text]()
            else:
                print(f"처리되지 않은 메시지: {message_text}")
        elif self.current_menu == "sub":
            if message_text == "뒤로 가기":
                self.set_main_menu()
            elif message_text == "1-1. 전략 수정":
                self.set_strategy_menu()
            elif message_text == "1-2. 금액 수정":
                self._send_text("새로운 자본금을 입력해주세요.")
                self.waiting_for_input = True
            elif message_text == "1-3. 시간 수정":
                self._send_text("시간 수정 기능은 아직 구현되지 않았습니다.")
            else:
                print(f"처리되지 않은 메시지: {message_text}")
        elif self.current_menu == "strategy":
            if message_text == "뒤로 가기":
                self.set_sub_menu()
            elif message_text in ["Sky Blue", "Dark Blue", "All Blue"]:
                self._send_text(f"{message_text} 전략이 선택되었습니다.")
                self.set_sub_menu()
            else:
                print(f"처리되지 않은 메시지: {message_text}")


    def register_handler(self, message, handler):
        self.message_handlers[message] = handler

    def wait_for_specific_message(self, messages, timeout=30):
        event = threading.Event()
        result = []

        def handler(message):
            result.append(message)
            event.set()

        for message in messages:
            self.register_handler(message, lambda m=message: handler(m))

        # 타임아웃 또는 메시지 수신까지 대기
        event.wait(timeout=timeout)

        for message in messages:
            self.message_handlers.pop(message, None)

        if not result:
            # 타임아웃 발생 시 'pass' 반환
            return 'pass'
        return result[0]


    def answer_callback_query(self, callback_query_id):
        url = self.base_url + "answerCallbackQuery"
        payload = {
            "callback_query_id": callback_query_id
        }
        requests.post(url, json=payload)


if __name__ == "__main__":
    print("hi")

        # # 차트 이미지 생성 및 전송
        # chart_image = self.generate_chart()
        # if chart_image:
        #     self.bot.send_chart(chart_image)