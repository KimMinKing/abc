import sqlalchemy
from sqlalchemy import create_engine, inspect
import pandas as pd

class DataManager:
    def __init__(self, db_connection_string):
        # MySQL 연결 문자열을 받아 엔진을 생성
        self.engine = create_engine(db_connection_string)

    def setup(self):
        # 데이터베이스 연결 확인
        with self.engine.connect() as conn:
            print("Database connection successful!")

    def table_exists(self, symbol, interval):
        table_name = f"{symbol.lower()}_{interval.lower()}"
        inspector = inspect(self.engine)
        return inspector.has_table(table_name)


    def load_data(self, symbol, interval, start_date, end_date):
        table_name = f"{symbol.lower()}_{interval.lower()}"
        query = f"""
        SELECT * FROM {table_name}
        WHERE time BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY time
        """
        
        # 데이터베이스에서 데이터 읽기
        with self.engine.connect() as conn:
            df = pd.read_sql(query, conn)
        
        return df
    
    def get_data(self, symbol, interval, start_date, end_date):
        start_timestamp = int(start_date.timestamp() * 1000)
        end_timestamp = int(end_date.timestamp() * 1000)
        
        table_name = f"{symbol.lower()}_{interval.lower()}"
        
        if self.table_exists(symbol, interval):
            print(f"Table {table_name} exists, checking data range...")
            query = f"""
            SELECT MIN(time) as min_time, MAX(time) as max_time FROM {table_name}
            WHERE time BETWEEN '{start_date}' AND '{end_date}'
            """
            
            with self.engine.connect() as conn:
                result = conn.execute(query).fetchone()
            
            min_time = result['min_time']
            max_time = result['max_time']
            print(f"Data range in database: {min_time} to {max_time}")
            
            if min_time and max_time:
                print(f"Data loaded from database for {symbol} {interval} between {start_date} and {end_date}")
                return self.load_data(symbol, interval, start_date, end_date)
        
        # 데이터가 없으면 API에서 데이터 가져오기
        print(f"No data found for {symbol} {interval} between {start_date} and {end_date}. Fetching from API...")
        api_data = self.fetch_api_data(symbol, interval, start_timestamp, end_timestamp)
        
        if not api_data:
            print("No data fetched from API.")
            return pd.DataFrame()
        
        # 데이터를 변환하고 저장
        df = self.convert_api_data(api_data, symbol)
        self.save_to_database(df, table_name)
        print(f"Data fetched from API and saved to database for {symbol} {interval} between {start_date} and {end_date}")
        return df


    def fetch_api_data(self, symbol, interval, start_timestamp, end_timestamp):
        # 여기에 실제 API 호출 코드를 추가
        # 예시로 빈 데이터를 반환합니다.
        return []

    def convert_api_data(self, api_data, symbol):
        formatted_data = []
        for entry in api_data:
            formatted_entry = {
                "symbol": symbol,
                "time": pd.to_datetime(entry[0], unit='ms', utc=True).tz_convert('Asia/Seoul'),
                "open": float(entry[1]),
                "high": float(entry[2]),
                "low": float(entry[3]),
                "close": float(entry[4]),
                "volume": float(entry[5]),
            }
            formatted_data.append(formatted_entry)

        return pd.DataFrame(formatted_data)

    def save_to_database(self, df, table_name):
        # 테이블이 없으면 생성 후 데이터 삽입
        df.to_sql(table_name, self.engine, if_exists='append', index=False)
        print(f"Data saved to {table_name}")

    # 심볼과 기간을 설정하고 데이터를 요청하는 함수
    def fetch_data_for_intervals(self,symbol, start_date, end_date):
        # 가져오고자 하는 주기를 설정 (1분봉과 5분봉)
        intervals = ['1m', '5m']
        data_frames = {}

        for interval in intervals:
            print(f"Fetching {interval} data for {symbol} from {start_date} to {end_date}")
            df = data_manager.get_data(symbol, interval, start_date, end_date)
            data_frames[interval] = df
            print(df.head())  # 각 데이터프레임의 일부를 출력하여 확인

        return data_frames

if __name__=='__main__':
    # DB 연결 문자열 및 API 클라이언트 설정
    db_connection_string = 'mysql+pymysql://root:s0107739@localhost:3306/mydatabase'

    # DataManager 인스턴스 생성
    data_manager = DataManager(db_connection_string)
    data_manager.setup()

    # 백테스트에 필요한 1분봉 및 5분봉 데이터 가져오기
    # symbol = 'btcusdt'
    # interval = '1m'
    # start_date = pd.to_datetime('2024-11-05 00:00:00')
    # end_date = pd.to_datetime('2024-11-09 00:00:00')

    # # 데이터 가져오기 (누락된 경우 API 호출 후 DB에 저장)
    # data_df = data_manager.get_data(symbol, interval, start_date, end_date)
    # print(data_df)


    symbol = 'btcusdt'
    start_date = pd.to_datetime('2024-11-05 00:00:00')
    end_date = pd.to_datetime('2024-11-09 00:00:00')
    data_frames = data_manager.fetch_data_for_intervals(symbol, start_date, end_date)