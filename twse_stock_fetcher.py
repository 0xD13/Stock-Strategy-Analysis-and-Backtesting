import pandas as pd
import requests
import json
from datetime import datetime, timedelta
import time
import os
import argparse

def get_stock_data(date, stock_no):
    url = f'https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={date}&stockNo={stock_no}'
    response = requests.get(url)
    if response.status_code == 200:
        content = json.loads(response.text)
        if 'data' in content and 'fields' in content:
            return pd.DataFrame(data=content['data'], columns=content['fields'])
    return None


def convert_date(tw_date):
    year = int(tw_date.split('/')[0]) + 1911
    month = tw_date.split('/')[1]
    day = tw_date.split('/')[2]
    return f'{year}-{month}-{day}'


def process_and_save_monthly(date, stock_no, output_file):
    date_str = date.strftime('%Y%m%d')
    print(f"正在抓取 {date_str} 的資料...")

    df = get_stock_data(date_str, stock_no)

    if df is not None:
        # 轉換欄位名稱並選擇需要的欄位
        df_processed = pd.DataFrame({
            'Date': df['日期'].apply(convert_date),
            'Open': df['開盤價'].str.replace(',', ''),
            'High': df['最高價'].str.replace(',', ''),
            'Low': df['最低價'].str.replace(',', ''),
            'Close': df['收盤價'].str.replace(',', ''),
            'Volume': df['成交股數'].str.replace(',', '')
        })

        # 如果檔案存在，讀取現有資料並過濾重複日期
        if os.path.exists(output_file):
            existing_df = pd.read_csv(output_file)
            # 找出新資料中不存在的日期
            new_dates = set(df_processed['Date']) - set(existing_df['Date'])
            # 只保留新日期的資料
            df_processed = df_processed[df_processed['Date'].isin(new_dates)]
            
            if len(df_processed) > 0:
                # 追加新資料
                df_processed.to_csv(output_file, index=False, mode='a', header=False)
                print(f"新增 {len(df_processed)} 筆資料")
            else:
                print("沒有新資料需要更新")
        else:
            # 如果檔案不存在，寫入所有資料
            df_processed.to_csv(output_file, index=False, mode='w')
            print(f"新增 {len(df_processed)} 筆資料")

        return True
    return False


def get_last_date_from_file(output_file):
    if os.path.exists(output_file):
        # 讀取檔案的最後一行
        df = pd.read_csv(output_file)
        last_date = df['Date'].iloc[-1]  # 取得最後一筆日期
        last_datetime = datetime.strptime(last_date, '%Y-%m-%d')
        # 返回下一天
        next_day = last_datetime + timedelta(days=1)
        return next_day
    return None


def fetch_stock_data(start_date, stock_no, output_file):
    # 檢查是否有現有檔案並取得最後日期
    last_date = get_last_date_from_file(output_file)

    if last_date:
        print(f"檢測到現有資料，最後日期為 {last_date.strftime('%Y-%m-%d')}，從隔天開始抓取")
        current_date = last_date
    else:
        print("沒有現有資料，從指定開始日期抓取")
        current_date = datetime.strptime(start_date, '%Y%m%d')

    end_date = datetime.now()

    while current_date <= end_date:
        success = process_and_save_monthly(current_date, stock_no, output_file)
        if success:
            print(f"{current_date.strftime('%Y-%m')} 資料處理完成")
        else:
            print(f"{current_date.strftime('%Y-%m')} 無資料或抓取失敗")

        # 移到下個月
        current_date = (current_date.replace(day=1) + timedelta(days=32)).replace(day=1)
        time.sleep(1)  # 避免過快請求


def get_taiwan_index_data(date):
    url = f'https://www.twse.com.tw/rwd/zh/TAIEX/MI_5MINS_HIST?date={date}'
    response = requests.get(url)
    if response.status_code == 200:
        content = json.loads(response.text)
        if 'data' in content and 'fields' in content:
            return pd.DataFrame(data=content['data'], columns=content['fields'])
    return None


def process_and_save_taiwan_index(date, output_file):
    date_str = date.strftime('%Y%m%d')
    print(f"正在抓取 {date_str} 的大盤資料...")

    df = get_taiwan_index_data(date_str)

    if df is not None:
        # 轉換欄位名稱並選擇需要的欄位
        df_processed = pd.DataFrame({
            'Date': df['日期'].apply(convert_date),
            'Open': df['開盤指數'].str.replace(',', ''),
            'High': df['最高指數'].str.replace(',', ''),
            'Low': df['最低指數'].str.replace(',', ''),
            'Close': df['收盤指數'].str.replace(',', '')
        })

        # 如果檔案不存在，寫入標頭；如果存在，追加資料
        if not os.path.exists(output_file):
            df_processed.to_csv(output_file, index=False, mode='w')
        else:
            df_processed.to_csv(output_file, index=False, mode='a', header=False)

        return True
    return False


def fetch_taiwan_index_data(start_date, output_file):
    # 檢查是否有現有檔案並取得最後日期
    last_date = get_last_date_from_file(output_file)

    if last_date:
        print(f"檢測到現有資料，最後日期為 {last_date.strftime('%Y-%m-%d')}，從隔天開始抓取")
        current_date = last_date
    else:
        print("沒有現有資料，從指定開始日期抓取")
        current_date = datetime.strptime(start_date, '%Y%m%d')

    end_date = datetime.now()

    while current_date <= end_date:
        success = process_and_save_taiwan_index(current_date, output_file)
        if success:
            print(f"{current_date.strftime('%Y-%m')} 資料處理完成")
        else:
            print(f"{current_date.strftime('%Y-%m')} 無資料或抓取失敗")

        # 移到下個月
        current_date = (current_date.replace(day=1) + timedelta(days=32)).replace(day=1)
        time.sleep(1)  # 避免過快請求


def main():
    # 設定命令列參數
    parser = argparse.ArgumentParser(description='抓取台灣證交所股票歷史資料')
    parser.add_argument('--stock_symbol', type=str, help='指定股票代號，例如 00631L')
    parser.add_argument('--start_date', type=str, default='20140101', help='開始日期，格式 YYYYMMDD，預設 20140101')
    parser.add_argument('--taiwan_index', action='store_true', help='是否抓取大盤指數資料')

    # 解析參數
    args = parser.parse_args()

    if not args.stock_symbol and not args.taiwan_index:
        parser.error("必須指定 --stock_symbol 或 --taiwan_index")

    start_date = args.start_date

    if args.taiwan_index:
        output_file = 'stockHistory/taiwan_index_data.csv'
        print("開始抓取大盤指數資料...")
        fetch_taiwan_index_data(start_date, output_file)
    else:
        stock_no = args.stock_symbol
        output_file = f'stockHistory/stock_{stock_no}_data.csv'
        print(f"開始抓取股票 {stock_no} 的資料...")
        fetch_stock_data(start_date, stock_no, output_file)

    print(f"所有資料已儲存至 {output_file}")


if __name__ == "__main__":
    main()