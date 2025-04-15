import pandas as pd
import numpy as np
from typing import Union, Tuple

# 設置 pandas 顯示選項
pd.set_option('display.max_rows', None)  # 顯示所有行
pd.set_option('display.max_columns', None)  # 顯示所有列
pd.set_option('display.width', None)  # 不限制顯示寬度
pd.set_option('display.max_colwidth', None)  # 不限制列寬度

def calculate_rsi(data: Union[pd.DataFrame, pd.Series], 
                 period: int = 14, 
                 column: str = 'Close',
                 wilder_method: bool = True) -> pd.Series:
    """
    計算相對強弱指標 (RSI)
    
    參數:
    data (pd.DataFrame or pd.Series): 包含收盤價的資料
    period (int): RSI 計算期間，預設為 14
    column (str): 如果輸入是 DataFrame，指定收盤價的欄位名稱
    wilder_method (bool): 是否使用 Wilder 原始方法計算，預設為 True
    
    返回:
    pd.Series: RSI 值的序列，索引為日期
    """
    # 確保輸入是 DataFrame 並有日期索引
    if isinstance(data, pd.Series):
        df = pd.DataFrame({'Close': data})
    else:
        df = data.copy()
    
    # 確保日期是索引
    if 'Date' in df.columns:
        df.set_index('Date', inplace=True)
    
    # 確保索引是日期格式
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    
    # 按日期排序
    df.sort_index(inplace=True)
    
    # 計算價格變動
    delta = df[column].diff()
    
    # 區分正負變動
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    if wilder_method:
        # 使用 Wilder 原始方法計算
        # 計算初始平均值
        avg_gain = np.nan_to_num(gain.rolling(window=period).mean())
        avg_loss = np.nan_to_num(loss.rolling(window=period).mean())
        
        # 從 period+1 開始應用 Wilder 平滑化方法
        for i in range(period, len(gain)):
            avg_gain[i] = (avg_gain[i-1] * (period-1) + gain[i]) / period
            avg_loss[i] = (avg_loss[i-1] * (period-1) + loss[i]) / period
        
        # 轉換回 Series，保持日期索引
        avg_gain = pd.Series(avg_gain, index=df.index)
        avg_loss = pd.Series(avg_loss, index=df.index)
    else:
        # 使用簡單移動平均計算
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
    
    # 計算相對強度 (RS)
    rs = avg_gain / avg_loss.replace(0, np.finfo(float).eps)  # 避免除以零
    
    # 計算RSI
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def calculate_kd(data: pd.DataFrame, 
                k_period: int = 9, 
                d_period: int = 3) -> Tuple[pd.Series, pd.Series]:
    """
    計算KD隨機指標 (Stochastic Oscillator)
    
    參數:
    data (pd.DataFrame): 包含 'High', 'Low', 'Close' 欄位的股票資料
    k_period (int): %K 的計算期間，預設為 9
    d_period (int): %D 的計算期間，預設為 3
    
    返回:
    Tuple[pd.Series, pd.Series]: (%K 值序列, %D 值序列)，索引為日期
    """
    # 確保日期是索引
    if 'Date' in data.columns:
        df = data.set_index('Date')
    else:
        df = data.copy()
    
    # 確保索引是日期格式
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    
    # 按日期排序
    df.sort_index(inplace=True)
    
    # 計算過去 k_period 天的最高價和最低價
    low_min = df['Low'].rolling(window=k_period).min()
    high_max = df['High'].rolling(window=k_period).max()
    
    # 計算 %K (Fast Stochastic)
    k = 100 * ((df['Close'] - low_min) / (high_max - low_min))
    
    # 計算 %D (Slow Stochastic)
    d = k.rolling(window=d_period).mean()
    
    return k, d


def calculate_macd(data: pd.DataFrame, 
                  fast_period: int = 12, 
                  slow_period: int = 26, 
                  signal_period: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    計算MACD指標
    
    參數:
    data (pd.DataFrame): 包含 'Close' 欄位的股票資料
    fast_period (int): 快速移動平均期間，預設為 12
    slow_period (int): 慢速移動平均期間，預設為 26
    signal_period (int): 訊號線期間，預設為 9
    
    返回:
    Tuple[pd.Series, pd.Series, pd.Series]: (MACD線, 訊號線, 柱狀圖)，索引為日期
    """
    # 確保日期是索引
    if 'Date' in data.columns:
        df = data.set_index('Date')
    else:
        df = data.copy()
    
    # 確保索引是日期格式
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    
    # 按日期排序
    df.sort_index(inplace=True)
    
    # 計算快速和慢速EMA
    fast_ema = df['Close'].ewm(span=fast_period, adjust=False).mean()
    slow_ema = df['Close'].ewm(span=slow_period, adjust=False).mean()
    
    # 計算MACD線
    macd_line = fast_ema - slow_ema
    
    # 計算訊號線
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    
    # 計算柱狀圖
    histogram = macd_line - signal_line
    
    return macd_line, signal_line, histogram


def calculate_bollinger_bands(data: pd.DataFrame, 
                            period: int = 20, 
                            std_dev: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    計算布林通道
    
    參數:
    data (pd.DataFrame): 包含 'Close' 欄位的股票資料
    period (int): 移動平均期間，預設為 20
    std_dev (float): 標準差倍數，預設為 2.0
    
    返回:
    Tuple[pd.Series, pd.Series, pd.Series]: (中軌, 上軌, 下軌)，索引為日期
    """
    # 確保日期是索引
    if 'Date' in data.columns:
        df = data.set_index('Date')
    else:
        df = data.copy()
    
    # 確保索引是日期格式
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    
    # 按日期排序
    df.sort_index(inplace=True)
    
    # 計算中軌 (20日移動平均)
    middle_band = df['Close'].rolling(window=period).mean()
    
    # 計算標準差
    std = df['Close'].rolling(window=period).std()
    
    # 計算上軌和下軌
    upper_band = middle_band + (std * std_dev)
    lower_band = middle_band - (std * std_dev)
    
    return middle_band, upper_band, lower_band


def calculate_technical_indicators(data: pd.DataFrame) -> pd.DataFrame:
    """
    計算所有技術指標並合併到原始資料中
    
    參數:
    data (pd.DataFrame): 包含 'Open', 'High', 'Low', 'Close' 欄位的股票資料
    
    返回:
    pd.DataFrame: 包含所有技術指標的資料，索引為日期
    """
    # 確保日期是索引
    if 'Date' in data.columns:
        df = data.set_index('Date')
    else:
        df = data.copy()
    
    # 確保索引是日期格式
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    
    # 按日期排序
    df.sort_index(inplace=True)
    
    # 計算 RSI
    df['RSI'] = calculate_rsi(df)
    
    # 計算 KD
    k, d = calculate_kd(df)
    df['K'] = k
    df['D'] = d
    
    # 計算 MACD
    macd_line, signal_line, histogram = calculate_macd(df)
    df['MACD'] = macd_line
    df['MACD_Signal'] = signal_line
    df['MACD_Hist'] = histogram
    
    # 計算布林通道
    middle_band, upper_band, lower_band = calculate_bollinger_bands(df)
    df['BB_Middle'] = middle_band
    df['BB_Upper'] = upper_band
    df['BB_Lower'] = lower_band
    
    return df 