# Stock Strategy Analysis and Backtesting

這是一個股票分析系統，主要進行各種策略的回測與分析。



## 功能特點

### 撈取台股資料
- 支援下載台股大盤指數和個股資料
- 可自定義下載時間範圍
- 資料格式包含：
  - 日期
  - 開盤價
  - 最高價
  - 最低價
  - 收盤價
- 自動處理資料格式轉換
- 支援自動更新機制（[詳細](#自動更新股票資料)）

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
├── data/                     # 市場資料目錄
│   └── twse/                 # 台股資料
│       ├── ^TWII.csv         # 大盤指數資料
│       └── 00631L.csv        # 個股資料
├── fetcher/                  # 資料抓取程式
│   └── twse_stock_fetcher.py
├── strategy/                 # 交易策略
│   └── rebalance_strategy.py # 資產再平衡策略
├── report/                   # 回測報告和圖表
├── requirements.txt          # 專案依賴套件
└── README.md                 # 專案說明文件
```


## 使用說明

### 1. 下載股票資料

#### 下載個股資料
```bash
python fetcher/twse_stock_fetcher.py --stock_symbol 2330 --start_date 20200101
```

#### 下載大盤指數資料
```bash
python fetcher/twse_stock_fetcher.py --taiwan_index --start_date 20200101
```

參數說明：
- `--stock_symbol`: 股票代碼（與 --taiwan_index 二選一）
- `--taiwan_index`: 是否下載大盤指數資料（與 --stock_symbol 二選一）
- `--start_date`: 開始日期，格式：YYYYMMDD（預設：20140101）

輸出檔案：
- 個股資料：`data/twse/{股票代碼}.csv`
- 大盤指數：`data/twse/^TWII.csv`

### 2. 執行資產再平衡分析

```bash
python strategy/rebalance_strategy.py --data_file data/twse/2330.csv --cash_ratio 0.5 --stock_ratio 0.5 --rebalance_threshold 0.5
```

#### 參數說明
- `--data_file`: 股票資料檔案（預設：data/twse/00631L.csv）
- `--initial_capital`: 初始資金（預設：1,000,000）
- `--cash_ratio`: 現金比例（預設：0.5）
- `--stock_ratio`: 股票比例（預設：0.5）
- `--rebalance_threshold`: 再平衡觸發閾值（預設：0.5）
- `--start_date`: 開始日期，格式：YYYY-MM-DD（選填）

#### 輸出檔案

- `report/portfolio_analysis_{股票代碼}_cash{現金比例}_stock{股票比例}_threshold{閾值}.png`：資產配置變化圖表
- `report/portfolio_analysis_{股票代碼}_cash{現金比例}_stock{股票比例}_threshold{閾值}.txt`：詳細分析報告

#### 報告內容
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

1. 確保 `data/twse` 目錄中有正確的股票資料檔案
2. 下載資料時請注意 API 請求頻率限制

## 未來改進

1. 加入其他交易策略（歡迎提供）
2. 加入更多市場撈取功能
3. 加入 技術分析工具
4. 實現自動化交易功能

## 自動更新股票資料

本專案提供自動更新股票資料的功能，使用 GitHub Actions 每天自動抓取最新的股票數據。  
更新時間設定為每天台灣時間 15:00（收盤後）

### 設定方法

1. 複製 `.github/workflows/update_stock_data.yml` 到你的專案中
2. 修改 workflow 文件中的股票代號，例如：
   ```yaml
   - name: Update stock data
     run: |
       # 更新大盤指數
       python fetcher/twse_stock_fetcher.py --taiwan_index
       
       # 更新指定的股票
       python fetcher/twse_stock_fetcher.py --stock_symbol 0050
       python fetcher/twse_stock_fetcher.py --stock_symbol 2330
   ```

> [!IMPORTANT]  
> 首次使用前請先手動抓取歷史資料，避免撈取請求過多或過久導致意外錯誤