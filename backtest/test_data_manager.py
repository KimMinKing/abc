# test_data_manager.py
import sqlite3
from datamanger import DataManager

# 테스트용 SQLite 데이터베이스 생성 (임시로 사용)
db_connection = sqlite3.connect(":memory:")  # 메모리 내에 임시 DB 생성
cursor = db_connection.cursor()

# 테스트용 테이블 생성
cursor.execute("""
CREATE TABLE market_data (
    date TEXT PRIMARY KEY,
    open REAL,
    high REAL,
    low REAL,
    close REAL
);
""")
db_connection.commit()

# DataManager 인스턴스 생성
data_manager = DataManager(db_connection)

# 데이터 가용성 확인 테스트 (초기에는 데이터가 없으므로 False 기대)
start_date = "2023-01-01"
end_date = "2023-01-31"
is_data_available = data_manager.check_data_availability(start_date, end_date)
print("Data availability (initial):", is_data_available)  # Expected output: False

# API를 통한 데이터 수집 시뮬레이션
# (실제로는 API에서 데이터를 받아오겠지만, 여기서는 임의의 데이터 삽입)
def mock_fetch_data_from_api(start_date, end_date):
    # 임의의 데이터를 반환
    return [
        ("2023-01-01", 100, 105, 95, 102),
        ("2023-01-02", 102, 106, 101, 104),
        # 더 많은 테스트 데이터 추가 가능
    ]

# DataManager 클래스에 mock 메서드 할당
data_manager.fetch_data_from_api = mock_fetch_data_from_api

# 데이터 수집 및 저장
data_manager.get_historical_data(start_date, end_date)

# 데이터가 MySQL에 저장되었는지 확인
is_data_available_after = data_manager.check_data_availability(start_date, end_date)
print("Data availability (after fetching):", is_data_available_after)  # Expected output: True

# 테스트 결과 출력
assert is_data_available == False, "Initial data availability should be False"
assert is_data_available_after == True, "Data should be available after fetching"
print("DataManager 테스트 성공")
