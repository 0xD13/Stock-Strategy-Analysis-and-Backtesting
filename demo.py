import pandas as pd
from technical_indicators import calculate_technical_indicators

# 讀取股票資料
df = pd.read_csv('stockHistory/stock_2330_data.csv')

# 計算所有技術指標
df_with_indicators = calculate_technical_indicators(df)

# 或者只計算特定指標
from technical_indicators import calculate_rsi, calculate_kd

rsi = calculate_rsi(df)
k, d = calculate_kd(df)
print(rsi)