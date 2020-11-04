# coding: utf-8


# mysql
DB_HOST = "127.0.0.1"
DB_PORT = 3306
DB_USER = "root"
DB_PASS = "iiiiiii"
DB_NAME = "new"
DB_URI = "mysql+pymysql://{user}:{passd}@{host}:{port}/{db}".\
    format(user=DB_USER,
           passd=DB_PASS,
           host=DB_HOST,
           port=DB_PORT,
           db=DB_NAME)

