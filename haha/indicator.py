from rest_api import BinanceAPI
import numpy as np
import pandas as pd
import time

class Indicator:
    def pine_script_indicatorsfs(self, data, slow=4, fast=9, signal=33):
        df= pd.DataFrame()

        df['maFast'] = self.ta_ema(data['volume'] * data['close'], fast) / self.ta_ema(data['volume'], fast)
        df['maSlow'] = self.ta_ema(data['volume'] * data['close'], slow) / self.ta_ema(data['volume'], slow)
        df['d'] = df['maSlow'] - df['maFast']
        df['maSignal'] = self.ta_ema(df['d'], signal)
        df['dm'] = df['d'] - df['maSignal']

        # Vectorized color calculation
        df['h_color'] = np.select(
            [df['dm'] >= 0, df['dm'] < 0],
            [np.where(df['dm'] > df['dm'].shift(1), 'g', 'orange'),
            np.where(df['dm'] < df['dm'].shift(1), 'r', 'orange')]
        )

        # Vectorized redgreen calculation
        df['redgreen'] = np.select(
            [df['h_color'] == 'r', df['h_color'] == 'g'],
            [1, 2],
            default=0
        )
        df['redgreen'] = df['redgreen'].replace(0, np.nan).ffill()

        # Vectorized count calculation
        color_change = (df['h_color'] != df['h_color'].shift()).cumsum()
        df['count'] = ((df['h_color'] == 'orange') & (df['h_color'].shift() != 'orange')).groupby(color_change).cumsum()

        # Vectorized high calculation
        df['high'] = np.nan
        for color in ['r', 'g']:
            mask = df['h_color'] == color
            groups = mask.ne(mask.shift()).cumsum()[mask]
            if color == 'r':
                df.loc[mask, 'high'] = df.loc[mask, 'dm'].groupby(groups).cummin()
            else:
                df.loc[mask, 'high'] = df.loc[mask, 'dm'].groupby(groups).cummax()
        
        df['high'] = df['high'].ffill()

        return df[['dm', 'h_color', 'redgreen', 'count', 'high']]


    def calculate_ultimate_momentum(self, df, rsi_length=14, cci_length=50, overbought_level=90, oversold_level=10, rsi_weight=50):
        try:

            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=rsi_length).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_length).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            position_between_levels_rsi = 100 * (rsi - oversold_level) / (overbought_level - oversold_level)

            typical_price = (df['high'] + df['low'] + df['close']) / 3
            sma_tp = typical_price.rolling(window=cci_length).mean()
            mad = typical_price.rolling(window=cci_length).apply(lambda x: np.abs(x - x.mean()).mean())
            cci = (typical_price - sma_tp) / (0.015 * mad)
            normalized_cci = 50 + 0.5 * cci
            position_between_levels_cci = normalized_cci

            ultimate = pd.DataFrame(index=df.index)
            ultimate['ulti_momentum'] = (position_between_levels_rsi * (rsi_weight / 100) + position_between_levels_cci * ((100 - rsi_weight) / 100))
            ultimate['color'] = np.where(ultimate['ulti_momentum'] > 50, 'red', 'green')

            # 색상 변경 지점 표시
            ultimate['change'] = ultimate['color'] != ultimate['color'].shift(1)

            return ultimate
        except Exception as e:
            print(f"Ultimate Momentum 지표 계산 중 오류 발생: {str(e)}")
            return None
        
    
    def pine_script_indicatorpercenthl(self, df, period=22, permin=2):
        try:
            

            percentHL = ((df['high'] - df['low']) / df['low']) * 100
            percentRed = np.where(df['open'] > df['close'], ((df['open'] - df['close']) / df['close']) * 100, 0)
            percentGreen = np.where(df['open'] < df['close'], ((df['close'] - df['open']) / df['open']) * 100, 0)

            avgHL = percentHL.rolling(window=period).mean()
            Bcolor = pd.Series('gray', index=df.index)

            condition = percentHL > avgHL
            green_condition = (percentHL * (1 - permin) < percentGreen) & condition
            red_condition = (percentHL * (1 - permin) < percentRed) & condition

            Bcolor[green_condition] = 'blue'
            Bcolor[red_condition] = 'red'

            return Bcolor
        except Exception as e:
            print(f"PercentHL 지표 계산 중 오류 발생: {str(e)}")
            return None

    @staticmethod
    def ta_ema(series, period):
        return series.ewm(span=period, adjust=False).mean()
    
    

    def calculate_smi(self, df, percent_k_length=22, percent_d_length=2):
        try:

            ll = df['low'].rolling(window=percent_k_length).min()
            hh = df['high'].rolling(window=percent_k_length).max()
            diff = hh - ll
            rdiff = df['close'] - (hh + ll) / 2

            def ema_nested(series, period):
                return series.ewm(span=period, adjust=False).mean().ewm(span=period, adjust=False).mean()

            avgrel = ema_nested(rdiff, percent_d_length)
            avgdiff = ema_nested(diff, percent_d_length)

            smi = np.where(avgdiff != 0, (avgrel / (avgdiff / 2) * 100), 0)
            smi_signal = pd.Series(smi).ewm(span=percent_d_length, adjust=False).mean()

            return pd.DataFrame({'SMI': smi, 'SMI_signal': smi_signal}, index=df.index)
        except Exception as e:
            print(f"SMI 지표 계산 중 오류 발생: {str(e)}")
            return None
        
    def calculate_wma(self,df, period = 12):

        """
        주어진 DataFrame에서 주어진 기간의 WMA(Weighted Moving Average)를 계산합니다.
        """
        def WMA(array, window):
            """
            주어진 array에서 WMA(Weighted Moving Average)를 계산합니다.
            """
            array = np.array(array)
            assert array.ndim == 1, "1차원 array만 입력할 수 있습니다."
            n = len(array)

            result = np.empty(n)
            result[:] = np.nan

            weight = np.arange(1, window + 1, 1)

            ma = []
            # 0부터 n-window까지
            for i in range(0, n - window + 1):
                A = np.sum(weight * array[i:i + window])
                B = np.sum(weight)
                m = A / B
                ma.append(m)

            result[window - 1:] = ma

            return result


        return pd.Series(WMA(df['close'].values, period))
    

    def setindicators(self, indicators,data):
        """인디케이터 설정"""
        # 출력할 최대 행 수를 None으로 설정하여 전체 출력 허용

        indicators['smi']=self.calculate_smi(data)
        indicators['fs']=self.pine_script_indicatorsfs(data, slow=6,fast=9,signal=15)
        indicators['fs2']=self.pine_script_indicatorsfs(data, slow=188,fast=200,signal=300)
        indicators['fs3']=self.pine_script_indicatorsfs(data, slow=6,fast=9,signal=15)
        indicators['percenthl'] = self.pine_script_indicatorpercenthl(data)
        indicators['wma12']=self.calculate_wma(data)
        indicators['wma26']=self.calculate_wma(data,26)
        indicators['below_wmas'] = (data['close'] < indicators['wma12']) & (data['close'] < indicators['wma26']) & \
                    (data['high'] < indicators['wma12']) & (data['high'] < indicators['wma26'])


        return indicators


# # 사용 예시
# if __name__ == "__main__":

#     api = BinanceAPI()
#     # datamanger=DataManager()
#     indi=Indicator()

#     indicators={
#         'fs': None,
#         'fs2': None,
#         'fs3': None,
#         'ultimate': None,
#         'percenthl': None,
#         'smi': None,
#         'wma12': None
#     }

#     try:
        
#         one_minute_data = api.get_klines("btcusdt", "1m")
#         onemin=datamanger.convert_api_data(one_minute_data, "btcusdt")
        
#         # 시작 시간 기록
#         start_time = time.time()

#         indicators['smi']=indi.calculate_smi(onemin)
#         indicators['fs']=indi.pine_script_indicatorsfs(onemin, slow=6,fast=9,signal=15)
#         indicators['fs2']=indi.pine_script_indicatorsfs(onemin, slow=188,fast=200,signal=300)
#         indicators['fs3']=indi.pine_script_indicatorsfs(onemin, slow=6,fast=9,signal=15)
#         indicators['percenthl'] = indi.pine_script_indicatorpercenthl(onemin)
#         indicators['wma12']=indi.calculate_wma(onemin)


#         # 종료 시간 기록
#         end_time = time.time()

#         # 걸린 시간 계산
#         elapsed_time = end_time - start_time

#         # 결과 출력
#         print(f"걸린 시간: {elapsed_time:.2f}초")
        
#     except Exception as e:
#         print(e)
