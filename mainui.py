import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from maintrading import MainTrading
from input_handler import InputHandler

class MyWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        uic.loadUi("window.ui", self)
        self.initUI()
        self.main = MainTrading()
        self.input=InputHandler()
        self.setcombo()     #콤보박스 값 채우기
        self.main.startdata()
        self.chartui()





    def initUI(self):

        # 버튼과 레이블 설정
        self.testtradingbtn.clicked.connect(self.test_trading)
        self.chartbtn.clicked.connect(self.chartui)
        self.checkdatabtn.clicked.connect(self.checkdatas)
        self.strategyaddbtn.clicked.connect(self.strategyadd)
        self.strategydelbtn.clicked.connect(self.strategydel)
        self.livetradingstartbtn.clicked.connect(self.start)
        self.checkstrategybtn.clicked.connect(self.checkstrategy)

    def checkdatas(self):
        pass

    def checkstrategy(self):
        self.input.show_check_strategies(self.main.strategies)


    def test_trading(self):
        # print(self.main.data_manager.data['1m'].tail(5))
        # 가장 최근의 True 인덱스 찾기
        recent_true_index = self.main.data_manager.indicators['5m']['abcstrategy'][::-1].idxmax()
        data=self.main.data_manager.data['5m'].copy()
        # DataFrame의 time 열을 인덱스로 설정
        print(f"가장 최근의 True 값은 {recent_true_index}번째입니다.")
        # print(f"날짜에 맞는 데이터 : {data.loc[recent_true_index]['high']}")

    def uicallback(self, interval,data):
        self.main.data_callback(interval,data)
        self.chartui()


    def start(self):
        pass


    def setcombo(self):

        #전략 콤보박스 설정
        strategys= self.input.show_strategy_menu()
        for i in strategys:
            self.strategylistcombo.addItems([i.__name__])

        #분봉 콤보박스 설정
        minutes=self.main.strategies.keys()
        self.minutecombo.addItems(minutes)

        #일단 테스트로 매일 넣는거임
        selected_item = '5m'+"-"+'abcStrategyShort'
        if selected_item and self.check_list(selected_item):    #중복 확인, 값 확인
            self.strategylist.addItem(selected_item)            #combobox에 직접 값 입력
            self.main.strategyadd('5m', 'abcStrategyShort')          #main에 전략 추가

        selected_item = '5m'+"-"+'abcStrategyLong'
        if selected_item and self.check_list(selected_item):    #중복 확인, 값 확인
            self.strategylist.addItem(selected_item)            #combobox에 직접 값 입력
            self.main.strategyadd('5m', 'abcStrategyLong')          #main에 전략 추가


        selected_item = '1m'+"-"+'abcStrategyShort'
        if selected_item and self.check_list(selected_item):    #중복 확인, 값 확인
            self.strategylist.addItem(selected_item)            #combobox에 직접 값 입력
            self.main.strategyadd('1m', 'abcStrategyShort')          #main에 전략 추가

    #전략 설정 후 추가
    def strategyadd(self):
        timeframe=self.minutecombo.currentText()                #타임프레임
        strategy=self.strategylistcombo.currentText()           #전략
        selected_item = timeframe+"-"+strategy
        if selected_item and self.check_list(selected_item):    #중복 확인, 값 확인
            self.strategylist.addItem(selected_item)            #combobox에 직접 값 입력
            self.main.strategyadd(timeframe, strategy)          #main에 전략 추가
            #self.main.strategies[timeframe].append(strategy)    #main에 전략 추가





    def strategydel(self):
        selected_items = self.strategylist.selectedItems()
        if not selected_items:      #선택된게 없으면 꺼져
            return

        for item in selected_items: #아이템을 가져와서
            timeframe, strategy= item.text().split("-")     #타임프레임 전략으로 분류
            print(f"{strategy} - {timeframe}")
            self.main.strategydel(timeframe, strategy)      #main에 들어있는 전략 제거
            self.strategylist.takeItem(self.strategylist.row(item)) #list에서 제거



    #전략이 들어있나 확인
    def check_list(self, addstrategy):
        # QListWidget에 들어있는 항목 출력
        item_count = self.strategylist.count()  # 항목 개수 확인
        

        for i in range(item_count):
            item = self.strategylist.item(i)  # 각 항목 가져오기
            if item.text() == addstrategy:
                return False
            
        return True


    def chartui(self):
        # 기존 범위 저장 (xlim, ylim)
        xlim_1m, ylim_1m = None, None
        xlim_5m, ylim_5m = None, None
        xlim_5m_2, ylim_5m_2 = None, None
        xlim_30m, ylim_30m = None, None
        xlim_1h, ylim_1h = None, None

        if hasattr(self, 'canvas1') and hasattr(self, 'canvas2') and hasattr(self, 'canvas3') and hasattr(self, 'canvas4') and hasattr(self, 'canvas5'):
            # 기존에 차트가 그려져 있었으면 현재 범위를 저장
            xlim_1m = self.canvas1.figure.axes[0].get_xlim()
            ylim_1m = self.canvas1.figure.axes[0].get_ylim()
            xlim_5m = self.canvas2.figure.axes[0].get_xlim()
            ylim_5m = self.canvas2.figure.axes[0].get_ylim()
            xlim_5m_2 = self.canvas5.figure.axes[0].get_xlim()
            ylim_5m_2 = self.canvas5.figure.axes[0].get_ylim()
            xlim_30m = self.canvas4.figure.axes[0].get_xlim()
            ylim_30m = self.canvas4.figure.axes[0].get_ylim()
            xlim_1h = self.canvas3.figure.axes[0].get_xlim()
            ylim_1h = self.canvas3.figure.axes[0].get_ylim()

        # 세 개의 Figure 객체를 가져옴 (1분, 5분, 1시간)
        fig_1m, fig_5m, fig_5m_2, fig30m, fig_1h = self.main.plot_charts()

        # chartWidget 초기화 (기존 위젯 제거)
        for widget, attr_name, fig in zip(
            [self.chartWidget1, self.chartWidget2, self.chartWidget3, self.chartWidget4, self.chartWidget5],
            ['canvas1', 'canvas2', 'canvas3', 'canvas4', 'canvas5'],
            [fig_1m, fig_5m, fig_1h, fig30m, fig_5m_2]
        ):
            if widget.layout() is not None:
                # 기존 레이아웃의 모든 아이템 제거
                while widget.layout().count():
                    item = widget.layout().takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
            else:
                # 레이아웃이 없는 경우 새로 생성
                widget.setLayout(QVBoxLayout())

            # 새로운 캔버스와 툴바 생성
            canvas = FigureCanvas(fig)
            toolbar = NavigationToolbar(canvas, widget)

            # 위젯에 툴바와 캔버스 추가
            widget.layout().addWidget(toolbar)
            widget.layout().addWidget(canvas)

            # 클래스 속성으로 저장
            setattr(self, attr_name, canvas)
            setattr(self, f'toolbar{attr_name[-1]}', toolbar)

            # 이전 범위 설정 (범위가 있을 경우)
            if (attr_name == 'canvas1' and xlim_1m is not None and ylim_1m is not None) or \
            (attr_name == 'canvas2' and xlim_5m is not None and ylim_5m is not None) or \
            (attr_name == 'canvas3' and xlim_1h is not None and ylim_1h is not None) or \
            (attr_name == 'canvas4' and xlim_30m is not None and ylim_30m is not None) or \
            (attr_name == 'canvas5' and xlim_5m_2 is not None and ylim_5m_2 is not None)          :
                if attr_name == 'canvas1':
                    canvas.figure.axes[0].set_xlim(xlim_1m)
                    canvas.figure.axes[0].set_ylim(ylim_1m)
                elif attr_name == 'canvas2':
                    canvas.figure.axes[0].set_xlim(xlim_5m)
                    canvas.figure.axes[0].set_ylim(ylim_5m)
                elif attr_name == 'canvas3':
                    canvas.figure.axes[0].set_xlim(xlim_1h)
                    canvas.figure.axes[0].set_ylim(ylim_1h)
                elif attr_name == 'canvas4':
                    canvas.figure.axes[0].set_xlim(xlim_30m)
                    canvas.figure.axes[0].set_ylim(ylim_30m)
                elif attr_name == 'canvas5':
                    canvas.figure.axes[0].set_xlim(xlim_5m_2)
                    canvas.figure.axes[0].set_ylim(ylim_5m_2)

            # 차트 새로고침
            canvas.draw()

            # 차트 이동(pan) 기능 자동 활성화
            if attr_name == 'canvas1':
                toolbar.pan()  # 1분봉 차트의 pan(이동) 기능 활성화
            else:
                toolbar.pan()  # 5분봉 차트의 pan(이동) 기능 활성화


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
