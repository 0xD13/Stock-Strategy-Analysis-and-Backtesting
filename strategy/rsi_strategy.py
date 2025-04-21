import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import argparse
import os
import sys

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.technical_indicators import calculate_rsi

class RSIStrategy:
    def __init__(self, data_file, initial_capital=1000000, oversold_threshold=30, 
                 overbought_threshold=70, rsi_period=14, start_date=None):
        # 讀取資料
        self.df = pd.read_csv(data_file)
        self.df['Date'] = pd.to_datetime(self.df['Date'])
        self.df.set_index('Date', inplace=True)
        
        # 如果指定開始日期，過濾資料
        if start_date:
            start_date = pd.to_datetime(start_date)
            self.df = self.df[self.df.index >= start_date]
        
        # 計算RSI
        self.df['RSI'] = calculate_rsi(self.df['Close'], period=rsi_period)
        
        # 初始化參數
        self.initial_capital = initial_capital
        self.oversold_threshold = oversold_threshold
        self.overbought_threshold = overbought_threshold
        self.rsi_period = rsi_period
        
        # 初始化變數
        self.portfolio_value = []
        self.current_cash = initial_capital
        self.current_stocks = 0
        self.trades = []
        
        # 設定記錄的起始日期（需要跳過RSI計算所需的初始期間）
        self.start_idx = self.rsi_period + 1  # 確保有足夠的數據來計算RSI
    
    def calculate_portfolio_value(self):
        # 跳過前面幾天，確保RSI已經計算好
        for i in range(self.start_idx, len(self.df)):
            current_date = self.df.index[i]
            current_price = self.df['Close'].iloc[i]
            current_rsi = self.df['RSI'].iloc[i]
            
            # 計算當前資產價值
            stock_value = self.current_stocks * current_price
            total_value = self.current_cash + stock_value
            
            # RSI策略判斷
            if current_rsi <= self.oversold_threshold and self.current_cash > 0:
                # RSI低於閾值，買進
                shares_to_buy = self.current_cash / current_price
                buy_value = shares_to_buy * current_price
                
                self.current_stocks += shares_to_buy
                self.current_cash -= buy_value
                
                self.trades.append({
                    'date': current_date,
                    'type': 'buy',
                    'price': current_price,
                    'rsi': current_rsi,
                    'shares': shares_to_buy,
                    'value': buy_value
                })
                
            elif current_rsi >= self.overbought_threshold and self.current_stocks > 0:
                # RSI高於閾值，賣出
                sell_value = self.current_stocks * current_price
                
                self.trades.append({
                    'date': current_date,
                    'type': 'sell',
                    'price': current_price,
                    'rsi': current_rsi,
                    'shares': self.current_stocks,
                    'value': sell_value
                })
                
                self.current_cash += sell_value
                self.current_stocks = 0
            
            # 記錄當日資產價值
            self.portfolio_value.append({
                'date': current_date,
                'total_value': total_value,
                'cash': self.current_cash,
                'stocks': stock_value,
                'rsi': current_rsi
            })
    
    def calculate_metrics(self):
        # 轉換為DataFrame
        portfolio_df = pd.DataFrame(self.portfolio_value)
        if len(portfolio_df) == 0:
            return {
                '總報酬率': "0.00%", 
                '年化報酬率': "0.00%",
                '最大回撤': "0.00%", 
                '交易次數': 0,
                '夏普比率': "0.00"
            }
            
        portfolio_df.set_index('date', inplace=True)
        
        # 計算報酬率
        portfolio_df['returns'] = portfolio_df['total_value'].pct_change()
        total_return = (portfolio_df['total_value'].iloc[-1] / self.initial_capital - 1) * 100
        
        # 計算最大回撤
        portfolio_df['cummax'] = portfolio_df['total_value'].cummax()
        portfolio_df['drawdown'] = (portfolio_df['total_value'] - portfolio_df['cummax']) / portfolio_df['cummax']
        max_drawdown = portfolio_df['drawdown'].min() * 100
        
        # 計算交易次數
        trades_df = pd.DataFrame(self.trades)
        num_trades = len(trades_df)
        
        # 計算年化報酬率
        days = (portfolio_df.index[-1] - portfolio_df.index[0]).days
        years = max(days / 365, 0.01)  # 避免除以零
        annual_return = ((1 + total_return/100) ** (1/years) - 1) * 100
        
        # 計算夏普比率
        risk_free_rate = 0.01  # 假設無風險利率1%
        if portfolio_df['returns'].std() > 0:
            excess_returns = portfolio_df['returns'] - risk_free_rate/252
            sharpe_ratio = np.sqrt(252) * excess_returns.mean() / excess_returns.std()
        else:
            sharpe_ratio = 0
        
        return {
            '總報酬率': f"{total_return:.2f}%",
            '年化報酬率': f"{annual_return:.2f}%",
            '最大回撤': f"{max_drawdown:.2f}%",
            '交易次數': num_trades,
            '夏普比率': f"{sharpe_ratio:.2f}"
        }
    
    def get_trade_details(self):
        trades_df = pd.DataFrame(self.trades)
        if len(trades_df) > 0:
            trades_df['date'] = pd.to_datetime(trades_df['date'])
            trades_df = trades_df.sort_values('date')
            trades_df['value'] = trades_df['value'].round(2)
            trades_df['price'] = trades_df['price'].round(2)
            trades_df['shares'] = trades_df['shares'].round(2)
            trades_df['rsi'] = trades_df['rsi'].round(2)
            return trades_df
        return None
    
    def plot_results(self, data_file, oversold_threshold, overbought_threshold, rsi_period, start_date):
        portfolio_df = pd.DataFrame(self.portfolio_value)
        if len(portfolio_df) == 0:
            print("沒有足夠數據來繪製圖表")
            return None
            
        portfolio_df.set_index('date', inplace=True)
        
        # 設定中文字體
        plt.rcParams['font.sans-serif'] = ['Noto Sans CJK TC', 'Noto Sans CJK JP', 'Noto Sans CJK KR', 'Noto Sans CJK SC', 'SimHei', 'Arial Unicode MS']
        plt.rcParams['axes.unicode_minus'] = False
        
        plt.figure(figsize=(12, 12))
        
        # 繪製總資產價值
        plt.subplot(3, 1, 1)
        plt.plot(portfolio_df.index, portfolio_df['total_value'], label='總資產價值')
        plt.title('資產價值趨勢')
        plt.xlabel('日期')
        plt.ylabel('價值')
        plt.legend()
        plt.grid(True)
        
        # 繪製現金和股票比例
        plt.subplot(3, 1, 2)
        plt.plot(portfolio_df.index, portfolio_df['cash'], label='現金')
        plt.plot(portfolio_df.index, portfolio_df['stocks'], label='股票')
        plt.title('現金 vs 股票 價值')
        plt.xlabel('日期')
        plt.ylabel('價值')
        plt.legend()
        plt.grid(True)
        
        # 繪製RSI和買賣訊號
        plt.subplot(3, 1, 3)
        plt.plot(portfolio_df.index, portfolio_df['rsi'], label='RSI')
        plt.axhline(y=oversold_threshold, color='g', linestyle='--', label=f'超賣閾值 ({oversold_threshold})')
        plt.axhline(y=overbought_threshold, color='r', linestyle='--', label=f'超買閾值 ({overbought_threshold})')
        
        # 添加買賣點
        trades_df = pd.DataFrame(self.trades)
        if len(trades_df) > 0:
            buy_signals = trades_df[trades_df['type'] == 'buy']
            sell_signals = trades_df[trades_df['type'] == 'sell']
            
            if len(buy_signals) > 0:
                plt.scatter(buy_signals['date'], buy_signals['rsi'], color='g', marker='^', s=100, label='買入訊號')
            
            if len(sell_signals) > 0:
                plt.scatter(sell_signals['date'], sell_signals['rsi'], color='r', marker='v', s=100, label='賣出訊號')
        
        plt.title('RSI 指標和交易訊號')
        plt.xlabel('日期')
        plt.ylabel('RSI')
        plt.legend()
        plt.grid(True)
        plt.ylim(0, 100)
        
        plt.tight_layout()
        
        # 確保輸出目錄存在
        output_dir = "report"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 生成圖表檔名
        stock_code = os.path.splitext(os.path.basename(data_file))[0]
        base_filename = f"rsi_strategy_{stock_code}_oversold{oversold_threshold}_overbought{overbought_threshold}_period{rsi_period}"
        if start_date:
            base_filename += f"_start{start_date.replace('-', '')}"
        filename = os.path.join(output_dir, base_filename + ".png")
        
        plt.savefig(filename)
        plt.close()
        return filename

def main():
    # 設定命令列參數
    parser = argparse.ArgumentParser(description='RSI策略分析')
    parser.add_argument('--data_file', type=str, default='data/twse/^TWII.csv', help='股票資料檔案')
    parser.add_argument('--initial_capital', type=float, default=1000000, help='初始資金')
    parser.add_argument('--oversold_threshold', type=float, default=30, help='RSI超賣閾值（低於此值買入）')
    parser.add_argument('--overbought_threshold', type=float, default=70, help='RSI超買閾值（高於此值賣出）')
    parser.add_argument('--rsi_period', type=int, default=14, help='RSI計算周期')
    parser.add_argument('--start_date', type=str, default=None, help='開始日期 (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    # 初始化策略
    strategy = RSIStrategy(
        data_file=args.data_file,
        initial_capital=args.initial_capital,
        oversold_threshold=args.oversold_threshold,
        overbought_threshold=args.overbought_threshold,
        rsi_period=args.rsi_period,
        start_date=args.start_date
    )
    
    # 執行策略
    strategy.calculate_portfolio_value()
    
    # 計算績效指標
    metrics = strategy.calculate_metrics()
    
    # 確保輸出目錄存在
    output_dir = "report"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 生成報告檔名
    stock_code = os.path.splitext(os.path.basename(args.data_file))[0]
    base_filename = f"rsi_strategy_{stock_code}_oversold{args.oversold_threshold}_overbought{args.overbought_threshold}_period{args.rsi_period}"
    if args.start_date:
        base_filename += f"_start{args.start_date.replace('-', '')}"
    
    # 開啟報告檔案
    report_filename = os.path.join(output_dir, base_filename + ".txt")
    with open(report_filename, 'w', encoding='utf-8') as f:
        # 寫入參數設定
        f.write("=== 參數設定 ===\n")
        f.write(f"股票資料: {args.data_file}\n")
        f.write(f"初始資金: {args.initial_capital:,.2f}\n")
        f.write(f"RSI超賣閾值: {args.oversold_threshold}\n")
        f.write(f"RSI超買閾值: {args.overbought_threshold}\n")
        f.write(f"RSI計算周期: {args.rsi_period}\n")
        if args.start_date:
            f.write(f"開始日期: {args.start_date}\n")
        f.write("\n")
        
        # 寫入績效指標
        f.write("=== 績效指標 ===\n")
        for metric, value in metrics.items():
            f.write(f"{metric}: {value}\n")
        f.write("\n")
        
        # 寫入交易明細
        f.write("=== 交易明細 ===\n")
        trades_df = strategy.get_trade_details()
        if trades_df is not None:
            f.write(trades_df.to_string())
        else:
            f.write("無交易記錄")
        f.write("\n\n")
        
        # 只有在有資產組合時才寫入最終資產配置
        if len(strategy.portfolio_value) > 0:
            final_portfolio = strategy.portfolio_value[-1]
            f.write("=== 最終資產配置 ===\n")
            f.write(f"持股價值: {final_portfolio['stocks']:,.2f}\n")
            f.write(f"現金量: {final_portfolio['cash']:,.2f}\n")
            f.write(f"總資產: {final_portfolio['total_value']:,.2f}\n")
            f.write(f"持股比例: {(final_portfolio['stocks'] / final_portfolio['total_value'] * 100 if final_portfolio['total_value'] > 0 else 0):.2f}%\n")
            f.write(f"現金比例: {(final_portfolio['cash'] / final_portfolio['total_value'] * 100 if final_portfolio['total_value'] > 0 else 0):.2f}%\n")
    
    # 繪製圖表
    chart_filename = strategy.plot_results(
        args.data_file,
        args.oversold_threshold,
        args.overbought_threshold,
        args.rsi_period,
        args.start_date
    )
    
    # 輸出到終端機
    print(f"\n報告已儲存為 {report_filename}")
    if chart_filename:
        print(f"圖表已儲存為 {chart_filename}")
    
    # 同時在終端機顯示最終資產配置
    if len(strategy.portfolio_value) > 0:
        final_portfolio = strategy.portfolio_value[-1]
        print("\n=== 最終資產配置 ===")
        print(f"持股價值: {final_portfolio['stocks']:,.2f}")
        print(f"現金量: {final_portfolio['cash']:,.2f}")
        print(f"總資產: {final_portfolio['total_value']:,.2f}")
        total_value = final_portfolio['total_value']
        if total_value > 0:
            print(f"持股比例: {(final_portfolio['stocks'] / total_value * 100):.2f}%")
            print(f"現金比例: {(final_portfolio['cash'] / total_value * 100):.2f}%")
        else:
            print("持股比例: 0.00%")
            print("現金比例: 0.00%")

if __name__ == "__main__":
    main() 