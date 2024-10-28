import sqlite3
import pandas as pd

# 데이터베이스 연결
def connect_db(db_name="market_data.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS market_data (
                        date TEXT PRIMARY KEY,
                        open REAL,
                        high REAL,
                        low REAL,
                        close REAL,
                        volume INTEGER
                    )""")
    conn.commit()
    return conn

# 데이터 확인 및 누락된 날짜 체크
def check_missing_dates(conn, start_date, end_date):
    cursor = conn.cursor()
    cursor.execute("SELECT date FROM market_data WHERE date BETWEEN ? AND ?", (start_date, end_date))
    stored_dates = {row[0] for row in cursor.fetchall()}
    
    # 모든 날짜 리스트 생성
    all_dates = pd.date_range(start=start_date, end=end_date).strftime('%Y-%m-%d')
    missing_dates = [date for date in all_dates if date not in stored_dates]
    return missing_dates

# API로 누락된 날짜의 데이터 가져오기 및 DB 저장
def get_data_from_api(start_date, end_date):
    # API 호출 대신 예시 데이터 사용
    api_data = [{"date": start_date, "open": 100, "high": 105, "low": 95, "close": 102, "volume": 1000}]
    return api_data

def save_data_to_db(conn, data):
    cursor = conn.cursor()
    for row in data:
        cursor.execute("INSERT OR REPLACE INTO market_data VALUES (?, ?, ?, ?, ?, ?)",
                       (row['date'], row['open'], row['high'], row['low'], row['close'], row['volume']))
    conn.commit()

# 데이터 불러오기 (필요 시 API 호출하여 누락 데이터 채우기)
def fetch_data(conn, start_date, end_date):
    # 1. 데이터베이스에서 필요한 범위의 데이터를 확인
    missing_dates = check_missing_dates(conn, start_date, end_date)
    
    # 2. 누락된 날짜가 있는 경우에만 API에서 데이터 가져와 저장
    if missing_dates:
        for date in missing_dates:
            api_data = get_data_from_api(date, date)  # 누락된 날짜의 데이터만 가져옴
            save_data_to_db(conn, api_data)
    
    # 3. 데이터베이스에서 최종 데이터를 다시 불러옴
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM market_data WHERE date BETWEEN ? AND ?", (start_date, end_date))
    return cursor.fetchall()

# 예제 실행
conn = connect_db()
start_date = "2024-12-01"
end_date = "2024-12-05"
data = fetch_data(conn, start_date, end_date)

for row in data:
    print(row)
conn.close()
