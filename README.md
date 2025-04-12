# AutoTrader

這是一個自動交易系統，主要實現資產再平衡策略。

## 功能特點

### 資產再平衡策略 (Rebalance Strategy)
- 維持固定比例的資產配置（如50:50的股票和現金）
- 當資產比例偏離目標時自動進行再平衡
- 可自定義：
  - 現金比例
  - 股票比例
  - 再平衡觸發閾值
  - 開始日期
- 提供詳細的交易記錄和績效分析
- 生成資產配置變化圖表

## 目錄結構

```
AutoTrader/
├── backtestReport/          # 回測報告和圖表輸出目錄
├── stockHistory/            # 股票歷史資料目錄
├── rebalance_analysis.py    # 資產再平衡分析程式
├── twse_stock_fetcher.py    # 台股資料下載程式
├── requirements.txt         # 專案依賴套件
└── README.md               # 專案說明文件
```

## 安裝需求

```bash
pip install -r requirements.txt
```

## 使用說明

### 1. 下載股票資料

```bash
python twse_stock_fetcher.py --stock 2330 --start_date 2020-01-01 --end_date 2024-04-12
```

參數說明：
- `--stock`: 股票代碼（必填）
- `--start_date`: 開始日期，格式：YYYY-MM-DD（必填）
- `--end_date`: 結束日期，格式：YYYY-MM-DD（必填）

### 2. 執行資產再平衡分析

```bash
python rebalance_analysis.py --data_file stock_2330_data.csv --cash_ratio 0.5 --stock_ratio 0.5 --rebalance_threshold 0.5
```

參數說明：
- `--data_file`: 股票資料檔案（預設：stock_2330_data.csv）
- `--initial_capital`: 初始資金（預設：1000000）
- `--cash_ratio`: 現金比例（預設：0.5）
- `--stock_ratio`: 股票比例（預設：0.5）
- `--rebalance_threshold`: 再平衡觸發閾值（預設：0.5）
- `--start_date`: 開始日期，格式：YYYY-MM-DD（選填）

## 輸出檔案

### 資產再平衡策略
- `backtestReport/portfolio_analysis_{股票代碼}_cash{現金比例}_stock{股票比例}_threshold{閾值}.png`：資產配置變化圖表
- `backtestReport/portfolio_analysis_{股票代碼}_cash{現金比例}_stock{股票比例}_threshold{閾值}.txt`：詳細分析報告

## 報告內容

### 資產再平衡策略報告包含：
1. 參數設定
2. 績效指標：
   - 總報酬率
   - 年化報酬率
   - 最大回撤
   - 夏普比率
   - 交易次數
3. 交易明細
4. 最終資產配置：
   - 持股價值
   - 現金量
   - 總資產
   - 持股比例
   - 現金比例

## 注意事項

1. 確保 `stockHistory` 目錄中有正確的股票資料檔案
2. 交易成本設定為0.4%（買賣各0.2%）
3. 建議先使用歷史數據進行回測
4. 實盤交易前請先小額測試
5. 定期檢視策略表現並進行優化

## 未來改進

1. 實現動態參數調整
2. 加入風險管理機制
3. 優化交易執行策略
4. 加入更多資產類別
5. 實現自動化交易功能

## Prerequisites

* **Python 3.9 or higher:** Ensure you have a compatible Python version installed.
* **pip:** Python's package installer.

## Installation

### Standard Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python twse_stock_fetcher.py --stock_symbol <stock_symbol>
```

* `--stock_symbol <stock_symbol>`: 指定股票代號，例如 00631L
* `--start_date YYYYMMDD`: 開始日期，預設 20140101