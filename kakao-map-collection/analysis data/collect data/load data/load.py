import pandas as pd
import os
import sqlalchemy
from sqlalchemy import create_engine
import psycopg2

class loading:
    def __init__(self, path):
        """
        df = excel path
        """
        self.dtypesql = {
            'store_id' : sqlalchemy.types.NUMERIC(),
            'store_name' : sqlalchemy.types.VARCHAR(50),
            'store_address' : sqlalchemy.types.VARCHAR(255),
            'store_day' : sqlalchemy.types.VARCHAR(10),
            'store_start_time' : sqlalchemy.types.TIME(),
            'store_end_time' : sqlalchemy.types.TIME(),
            'store_tel' : sqlalchemy.types.VARCHAR(20),
            'store_score' : sqlalchemy.types.NUMERIC(),
            'store_category' : sqlalchemy.types.VARCHAR(50)
        }

        self.url = "postgresql://postgres:1234@localhost:5433/lunch"
        self.conn = psycopg2.connect(self.url)
        self.df = pd.read_excel(path)
        self.df = self.df[["맛집명","주소","영업일","영업 시작시간","영업 종료시간","전화번호", "평점","업종"]]
        self.df = self.df.rename(columns={"맛집명":"store_name", "주소":"store_address", "영업일":"store_day", "영업 시작시간":"store_start_time", "영업 종료시간":"store_end_time", "전화번호":"store_tel", "평점":"store_score", "업종":"store_category"})
        self.df["store_id"] = range(len(self.df))
        self.engine = create_engine(self.url)

    def load(self, name, chunksize, if_exists):
        """
        name = database table name \n
        chunksize = memory size settings \n
        if_exists = append or replace
        """
        self.df.to_sql(name = name, con=self.engine, schema='public', chunksize=chunksize,
        if_exists=if_exists, index = False, dtype=self.dtypesql, method='multi')