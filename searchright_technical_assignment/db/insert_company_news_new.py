from sqlalchemy import create_engine

DATABASE_URL = "postgresql+psycopg2://searchright:searchright@localhost:5432/searchright"
engine = create_engine(DATABASE_URL)
conn = engine.connect()
print("연결 성공")
