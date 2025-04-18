import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import sys
import os

def calculate_future_payment_capacity(row):
    """
    計算未來配息能力
    計算方式：(Nav-30)/Dividend/Payouts Years
    """
    nav = float(row['NAV'])
    dividend = float(row['Dividend'])
    payouts = float(row['Payouts Years'])
    
    return (nav - 30) / dividend / payouts

def analyze_dividend_payment_capacity(stock_symbol):
    """
    分析 ETF 的未來配息能力
    使用淨值、配息金額和配息次數來評估未來的配息能力
    
    Args:
        stock_symbol (str): 股票代號，例如 '00713'
    """
    # 構建檔案路徑
    input_file = f"data/twse/dividend/{stock_symbol}.csv"
    
    # 檢查檔案是否存在
    if not os.path.exists(input_file):
        print(f"錯誤：找不到檔案 {input_file}")
        return None
    
    # 讀取 CSV 檔案
    df = pd.read_csv(input_file)
    
    # 將日期轉換為 datetime 類型
    df['Ex-Dividend Date'] = pd.to_datetime(df['Ex-Dividend Date'])
    
    # 計算未來配息能力指標
    df['Future_Payment_Capacity'] = df.apply(calculate_future_payment_capacity, axis=1)
    
    # 設定中文字體
    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
    plt.rcParams['axes.unicode_minus'] = False
    
    # 創建圖表來視覺化分析結果
    plt.figure(figsize=(12, 6))
    plt.plot(df['Ex-Dividend Date'], df['Future_Payment_Capacity'], 
            marker='o', linestyle='-', linewidth=2)
    
    # 設定圖表標題和軸標籤
    plt.title(f'{stock_symbol} 元大高息低波 ETF 未來配息能力', fontsize=14)
    plt.xlabel('除息日期', fontsize=12)
    plt.ylabel('未來配息能力指標', fontsize=12)
    
    # 旋轉 x 軸標籤以提高可讀性
    plt.xticks(rotation=45)
    
    # 添加網格輔助線
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # 調整布局
    plt.tight_layout()
    
    # 確保輸出目錄存在
    os.makedirs('report', exist_ok=True)
    
    # 儲存分析結果
    output_file = f'report/future_dividend_payment_capacity_{stock_symbol}.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"分析結果已儲存至 {output_file}")

    # 返回分析後的數據框
    return df

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("請提供股票代號")
        sys.exit(1)
    
    stock_symbol = sys.argv[1]
    result_df = analyze_dividend_payment_capacity(stock_symbol) 