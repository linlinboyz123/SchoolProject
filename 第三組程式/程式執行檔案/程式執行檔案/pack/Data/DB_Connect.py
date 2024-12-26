import os
import sys
import mysql.connector as db
import random

def Get_Config():
    config = {}
    # 從 'Data/config.txt' 文件讀取配置
    with open('Data/config.txt', 'r') as f:
        for line in f:
            key, value = line.strip().split('=')
            config[key.strip()] = value.strip()
    return config

def Test_Connect():
    try:
        config = Get_Config()
        # 使用配置進行數據庫連接
        connect = db.connect(
            host=config['host'],
            user=config['user'],
            password=config['password'],
            database=config['database']
        )
        print("連接成功")
    except db.Error as error:
        print("出現錯誤:", error)
    finally:
        # 關閉連接
        if connect.is_connected():
            connect.close()

def Get_Topic_And_Errors():
    #從資料庫中隨機選擇一個題目及其錯字和錯字位置。
    try:
        config = Get_Config()
        connect = db.connect(
            host=config['host'],
            user=config['user'],
            password=config['password'],
            database=config['database']
        )
        cursor = connect.cursor()

        # 隨機選擇一個題目編號
        query = """
            SELECT 題目, 錯字, 錯字位置 
            FROM topic 
            ORDER BY RAND() 
            LIMIT 1
        """
        cursor.execute(query)

        rows = cursor.fetchall()
        topics = []
        errors = []
        error_positions = []

        for row in rows:
            topic, error, error_position = row
            topics.append(topic)
            errors.append(error)
            error_positions.append(error_position)

        return topics, errors, error_positions

    except db.Error as error:
        print("資料庫錯誤:", error)
        return [], [], []
    finally:
        if connect.is_connected():
            cursor.close()
            connect.close()
