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
        # self.checkdatabtn.clicked.connect(self.checkdatas)
        self.strategyaddbtn.clicked.connect(self.strategyadd)
        self.strategydelbtn.clicked.connect(self.strategydel)
        self.livetradingstartbtn.clicked.connect(self.start)
        self.checkstrategybtn.clicked.connect(self.checkstrategy)

    def checkstrategy(self):
        self.input.show_check_strategies(self.main.strategies)


    def test_trading(self):
        print(self.main.data_manager.data['1m'].tail(5))


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
        print(f"Total items: {item_count}")

        for i in range(item_count):
            item = self.strategylist.item(i)  # 각 항목 가져오기
            if item.text() == addstrategy:
                return False
            
        return True

    def chartui(self):

            # 기존 범위 저장 (xlim, ylim)
            xlim_1m, ylim_1m = None, None
            xlim_5m, ylim_5m = None, None

            if hasattr(self, 'canvas1') and hasattr(self, 'canvas2'):
                # 기존에 차트가 그려져 있었으면 현재 범위를 저장
                xlim_1m = self.canvas1.figure.axes[0].get_xlim()
                ylim_1m = self.canvas1.figure.axes[0].get_ylim()
                xlim_5m = self.canvas2.figure.axes[0].get_xlim()
                ylim_5m = self.canvas2.figure.axes[0].get_ylim()

            fig_1m, fig_5m = self.main.plot_charts()  # 두 개의 Figure 객체를 가져옴

            # chartWidget 초기화 (기존 위젯 제거)
            for widget in [self.chartWidget1, self.chartWidget2]:
                if widget.layout() is not None:
                    
                    for i in reversed(range(widget.layout().count())):
                        widget_to_remove = widget.layout().itemAt(i).widget()
                        if widget_to_remove is not None:
                            widget_to_remove.deleteLater()



            # 1분봉 차트
            self.canvas1 = FigureCanvas(fig_1m)
            self.toolbar1 = NavigationToolbar(self.canvas1, self.chartWidget1)
            self.chartWidget1.setLayout(QVBoxLayout())
            self.chartWidget1.layout().addWidget(self.toolbar1)
            self.chartWidget1.layout().addWidget(self.canvas1)

            # 5분봉 차트
            self.canvas2 = FigureCanvas(fig_5m)
            self.toolbar2 = NavigationToolbar(self.canvas2, self.chartWidget2)
            self.chartWidget2.setLayout(QVBoxLayout())
            self.chartWidget2.layout().addWidget(self.toolbar2)
            self.chartWidget2.layout().addWidget(self.canvas2)

            # 이전 범위 설정 (범위가 있을 경우)
            if xlim_1m and ylim_1m:
                self.canvas1.figure.axes[0].set_xlim(xlim_1m)
                self.canvas1.figure.axes[0].set_ylim(ylim_1m)

            if xlim_5m and ylim_5m:
                self.canvas2.figure.axes[0].set_xlim(xlim_5m)
                self.canvas2.figure.axes[0].set_ylim(ylim_5m)

            # 차트 새로고침
            self.canvas1.draw()
            self.canvas2.draw()

                # 차트 이동(pan) 기능 자동 활성화
            self.toolbar1.pan()  # 1분봉 차트의 pan(이동) 기능 활성화
            self.toolbar2.pan()  # 5분봉 차트의 pan(이동) 기능 활성화


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
