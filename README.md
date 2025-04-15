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
└── README.md                # 專案說明文件
```

## 安裝需求

```bash
pip install -r requirements.txt
```

## 使用說明

### 1. 下載股票資料

#### 下載個股資料
```bash
python twse_stock_fetcher.py --stock_symbol 2330 --start_date 20200101
```

#### 下載大盤指數資料
```bash
python twse_stock_fetcher.py --taiwan_index --start_date 20200101
```

參數說明：
- `--stock_symbol`: 股票代碼（與 --taiwan_index 二選一）
- `--taiwan_index`: 是否下載大盤指數資料（與 --stock_symbol 二選一）
- `--start_date`: 開始日期，格式：YYYYMMDD（預設：20140101）

輸出檔案：
- 個股資料：`stockHistory/stock_{股票代碼}_data.csv`
- 大盤指數：`stockHistory/taiwan_index_data.csv`

### 2. 執行資產再平衡分析

```bash
python rebalance_analysis.py --data_file stock_2330_data.csv --cash_ratio 0.5 --stock_ratio 0.5 --rebalance_threshold 0.5
```

參數說明：
- `--data_file`: 股票資料檔案（預設：stock_2330_data.csv）
- `--initial_capital`: 初始資金（預設：1,000,000）
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
2. 下載資料時請注意 API 請求頻率限制
3. 建議先使用歷史數據進行回測
4. 實盤交易前請先小額測試
5. 定期檢視策略表現並進行優化

## 未來改進

1. 實現動態參數調整
2. 加入風險管理機制
3. 優化交易執行策略
4. 加入更多資產類別
5. 實現自動化交易功能

## 自動更新股票資料

本專案提供自動更新股票資料的功能，使用 GitHub Actions 每天自動抓取最新的股票數據。

### 設定方法

1. 複製 `.github/workflows/update_stock_data.yml` 到你的專案中
2. 修改 workflow 文件中的股票代號，例如：
   ```yaml
   - name: Update stock data
     run: |
       # 更新大盤指數
       python twse_stock_fetcher.py --taiwan_index
       
       # 更新指定的股票
       python twse_stock_fetcher.py --stock_symbol 0050
       python twse_stock_fetcher.py --stock_symbol 2330
   ```

### 重要注意事項

1. **首次使用前請先手動抓取歷史資料**：
   ```bash
   # 抓取大盤指數歷史資料
   python twse_stock_fetcher.py --taiwan_index --start_date 20140101
   
   # 抓取個股歷史資料
   python twse_stock_fetcher.py --stock_symbol 0050 --start_date 20140101
   ```
   
   這是因為：
   - 證交所 API 有請求頻率限制
   - 自動更新只會抓取最新資料
   - 建議先手動抓取完整歷史資料，避免被鎖 IP

2. 更新時間設定為每天台灣時間 15:00（收盤後）
3. 資料會保存在 `stockHistory` 目錄下
4. 可以手動觸發更新（在 GitHub Actions 頁面點擊 "Run workflow"）

### 資料格式

- 大盤指數：`stockHistory/taiwan_index_data.csv`
- 個股資料：`stockHistory/stock_XXXX_data.csv`

### 常見問題

1. **為什麼要手動抓取歷史資料？**
   - 避免頻繁請求被證交所鎖 IP
   - 確保有完整的歷史資料
   - 自動更新只會抓取最新資料

2. **如何修改更新頻率？**
   - 修改 workflow 中的 cron 設定
   - 例如：改為每週更新 `0 7 * * 1`（每週一 15:00）

3. **如何添加更多股票？**
   - 在 workflow 中添加新的 `--stock_symbol` 命令
   - 記得先手動抓取該股票的歷史資料