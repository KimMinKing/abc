import mplfinance as mpf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates  # mdates 모듈 추가

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

def plot_candlestick_charts(df_1m, df_5m, indicators):
    """
    1분봉과 5분봉 차트를 각각의 Figure 객체로 반환하는 함수.
    """
    # 캔들 색상을 반대로 설정 (상승: 빨간색, 하락: 초록색)
    market_colors = mpf.make_marketcolors(up='r', down='g', edge='inherit', wick='inherit', volume='inherit')
    style = mpf.make_mpf_style(marketcolors=market_colors)

    # 5분봉 차트용 Figure 생성
    fig_5m, ax_5m = plt.subplots(figsize=(10, 5))
    # ax_vol_5m = fig_5m.add_subplot(212)  # 볼륨 차트 추가


    


    # 마커 추가 로직
    def add_markers(df, interval):
        #12,26wma보다 가격이 낮으면 마커 추가.
        # True인 부분에만 마커를 그릴 위치를 설정 (low 값의 약간 아래에 표시)
        indicators[interval]['below_wmas'].index = df['low'].index

        marker_positions = df['low'][indicators[interval]['below_wmas']] - 0.001 * df['low']
        return marker_positions

    def abc_markers(df ,interval):
        #abc 빨간색 마커 추가
        indicators[interval]['abc'].index = df['high'].index
        marker_positions = df['high'][indicators[interval]['abc']] + 0.001 * df['high']
        return marker_positions
    
    def abc_strategy_markers(df ,interval):
        #abc의 전략을 쉽게 보기 위한 마커 추가
        indicators[interval]['abcstrategy'].index = df['high'].index
        marker_positions = df['high'][indicators[interval]['abcstrategy']] + 0.002 * df['high']
        return marker_positions
    
    def spear_markers(df ,interval):
        #주황색 spear 추가 아마 fs2의 h_color일거임.
        indicators[interval]['orangespear'].index = df['low'].index
        marker_positions = df['low'][indicators[interval]['orangespear']] - 0.002 * df['low']
        return marker_positions
    
    def triangleup_markers(df ,interval):
        #그냥 h_color의 색을 가져왔나?
        indicators[interval]['triangleup'].index = df['low'].index
        marker_positions = df['low'][indicators[interval]['triangleup']] - 0.0023 * df['low']
        return marker_positions

    # 5분봉 차트
    if not df_5m.empty:
        # x축을 마지막 100개로 제한
        ax_5m.set_xlim(df_5m.index[-100], df_5m.index[-1])  # 마지막 100개만 보이도록 설정
        df_5m = df_5m.set_index(pd.DatetimeIndex(df_5m['time']))

        #5분봉 차트, 마커 추가
        add_plots_5m = [
            mpf.make_addplot(indicators['5m']['wma12'], color='blue', ax=ax_5m),
            mpf.make_addplot(indicators['5m']['wma26'], color='orange', ax=ax_5m),
            mpf.make_addplot(add_markers(df_5m,'5m'), type='scatter', marker='^', markersize=10, color='g', ax=ax_5m),  # 마커 추가
            mpf.make_addplot(abc_markers(df_5m,'5m'), type='scatter', marker='^', markersize=10, color='red', ax=ax_5m),  # 마커 추가
            mpf.make_addplot(spear_markers(df_5m,'5m'), type='scatter', marker='|', markersize=18, color='orange', ax=ax_5m),  # 마커 추가
            mpf.make_addplot(triangleup_markers(df_5m,'5m'), type='scatter', marker='^', markersize=18, color='orange', ax=ax_5m),  # 마커 추가
            mpf.make_addplot(abc_strategy_markers(df_5m,'5m'), type='scatter', marker='^', markersize=20, color='blue', ax=ax_5m),  # 마커 추가
            ]

        mpf.plot(df_5m, type='candle', warn_too_much_data=1000, style=style, ax=ax_5m, addplot=add_plots_5m,  ylabel='', xlabel='')


        # x축 날짜 포맷 변경
        # ax_5m.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))  # 시간만 표시
        # ax_5m.xaxis.set_major_locator(mdates.MinuteLocator(interval=5))  # 5분 간격으로 표시
        plt.setp(ax_5m.xaxis.get_majorticklabels(), rotation=0)  # 기울임 제거

    plt.tight_layout()

    # 1분봉 차트용 Figure 생성
    fig_1m, ax_1m = plt.subplots(figsize=(10, 5))
    # ax_vol_1m = fig_1m.add_subplot(212)  # 볼륨 차트 추가

    # 1분봉 차트
    if not df_1m.empty:
        ax_1m.set_xlim(df_1m.index[-100], df_1m.index[-1])  # 마지막 100개만 보이도록 설정
        df_1m = df_1m.set_index(pd.DatetimeIndex(df_1m['time']))
        
        add_plots_1m = [
            mpf.make_addplot(indicators['1m']['wma12'], color='blue', ax=ax_1m),
            mpf.make_addplot(indicators['1m']['wma26'], color='orange', ax=ax_1m),
            mpf.make_addplot(add_markers(df_1m,'1m'), type='scatter', marker='^', markersize=10, color='green', ax=ax_1m),  # 마커 추가
            mpf.make_addplot(abc_markers(df_1m,'1m'), type='scatter', marker='^', markersize=10, color='red', ax=ax_1m)  # 마커 추가
        ]

        mpf.plot(df_1m, type='candle',  warn_too_much_data= 1000, style=style, ax=ax_1m, addplot=add_plots_1m, ylabel='', xlabel='')
        plt.setp(ax_1m.xaxis.get_majorticklabels(), rotation=0)  # 기울임 제거

    plt.tight_layout()
    plt.close(fig_1m)
    plt.close(fig_5m)
    return fig_1m, fig_5m  # 두 개의 Figure 객체를 반환
