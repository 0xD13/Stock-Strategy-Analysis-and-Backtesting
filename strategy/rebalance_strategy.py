import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import argparse
import os

class RebalanceStrategy:
    def __init__(self, data_file, initial_capital=1000000, cash_ratio=0.5, stock_ratio=0.5, rebalance_threshold=0.5, start_date=None):
        # 讀取資料
        self.df = pd.read_csv(data_file)
        self.df['Date'] = pd.to_datetime(self.df['Date'])
        self.df.set_index('Date', inplace=True)
        
        # 如果指定開始日期，過濾資料
        if start_date:
            start_date = pd.to_datetime(start_date)
            self.df = self.df[self.df.index >= start_date]
        
        # 初始化參數
        self.initial_capital = initial_capital
        self.cash_ratio = cash_ratio
        self.stock_ratio = stock_ratio
        self.rebalance_threshold = rebalance_threshold
        
        # 初始化變數
        self.portfolio_value = []
        self.current_cash = initial_capital * self.cash_ratio
        self.last_rebalance_price = self.df['Close'].iloc[0]
        self.current_stocks = initial_capital * self.stock_ratio / self.df['Close'].iloc[0]
        self.trades = [{
            'date': self.df.index[0],
            'type': 'buy',
            'price': self.last_rebalance_price,
            'shares': self.current_stocks,
            'value': initial_capital * self.stock_ratio
        }]
    
    def calculate_portfolio_value(self):
        for i in range(len(self.df)):
            current_price = self.df['Close'].iloc[i]
            current_date = self.df.index[i]
            
            # 計算當前資產價值
            stock_value = self.current_stocks * current_price
            total_value = self.current_cash + stock_value
            
            # 檢查是否需要再平衡
            price_change = abs((current_price - self.last_rebalance_price) / self.last_rebalance_price)
            
            if price_change >= self.rebalance_threshold:
                # 計算目標價值
                target_value = total_value / 2
                
                # 執行再平衡
                if stock_value > target_value:
                    # 賣出多餘股票
                    excess_value = stock_value - target_value
                    shares_to_sell = excess_value / current_price
                    self.current_stocks -= shares_to_sell
                    self.current_cash += excess_value
                    self.trades.append({
                        'date': current_date,
                        'type': 'sell',
                        'price': current_price,
                        'shares': shares_to_sell,
                        'value': excess_value
                    })
                elif self.current_cash > target_value:
                    # 買入不足股票
                    deficit_value = target_value - stock_value
                    shares_to_buy = deficit_value / current_price
                    self.current_stocks += shares_to_buy
                    self.current_cash -= deficit_value
                    self.trades.append({
                        'date': current_date,
                        'type': 'buy',
                        'price': current_price,
                        'shares': shares_to_buy,
                        'value': deficit_value
                    })
                
                self.last_rebalance_price = current_price
            
            # 記錄當日資產價值
            self.portfolio_value.append({
                'date': current_date,
                'total_value': total_value,
                'cash': self.current_cash,
                'stocks': stock_value
            })
    
    def calculate_metrics(self):
        # 轉換為DataFrame
        portfolio_df = pd.DataFrame(self.portfolio_value)
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
        years = days / 365
        annual_return = ((1 + total_return/100) ** (1/years) - 1) * 100
        
        # 計算夏普比率
        risk_free_rate = 0.01  # 假設無風險利率1%
        excess_returns = portfolio_df['returns'] - risk_free_rate/252
        sharpe_ratio = np.sqrt(252) * excess_returns.mean() / excess_returns.std()
        
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
            return trades_df
        return None
    
    def plot_results(self, data_file, cash_ratio, stock_ratio, rebalance_threshold, start_date):
        portfolio_df = pd.DataFrame(self.portfolio_value)
        portfolio_df.set_index('date', inplace=True)
        
        plt.figure(figsize=(12, 8))
        
        # 繪製總資產價值
        plt.subplot(2, 1, 1)
        plt.plot(portfolio_df.index, portfolio_df['total_value'], label='Total Portfolio Value')
        plt.title('Portfolio Value Trend')
        plt.xlabel('Date')
        plt.ylabel('Value')
        plt.legend()
        plt.grid(True)
        
        # 繪製現金和股票比例
        plt.subplot(2, 1, 2)
        plt.plot(portfolio_df.index, portfolio_df['cash'], label='Cash')
        plt.plot(portfolio_df.index, portfolio_df['stocks'], label='Stocks')
        plt.title('Cash vs Stocks Value')
        plt.xlabel('Date')
        plt.ylabel('Value')
        plt.legend()
        plt.grid(True)
        
        plt.tight_layout()
        
        # 確保輸出目錄存在
        output_dir = "report"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 生成圖表檔名
        stock_code = os.path.splitext(os.path.basename(data_file))[0]
        base_filename = f"portfolio_analysis_{stock_code}_cash{cash_ratio}_stock{stock_ratio}_threshold{rebalance_threshold}"
        if start_date:
            base_filename += f"_start{start_date.replace('-', '')}"
        filename = os.path.join(output_dir, base_filename + ".png")
        
        plt.savefig(filename)
        plt.close()
        return filename

def main():
    # 設定命令列參數
    parser = argparse.ArgumentParser(description='資產再平衡策略分析')
    parser.add_argument('--data_file', type=str, default='data/twse/00631L.csv', help='股票資料檔案')
    parser.add_argument('--initial_capital', type=float, default=1000000, help='初始資金')
    parser.add_argument('--cash_ratio', type=float, default=0.5, help='現金比例')
    parser.add_argument('--stock_ratio', type=float, default=0.5, help='股票比例')
    parser.add_argument('--rebalance_threshold', type=float, default=0.5, help='再平衡觸發閾值')
    parser.add_argument('--start_date', type=str, default=None, help='開始日期 (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    # 初始化策略
    strategy = RebalanceStrategy(
        data_file=args.data_file,
        initial_capital=args.initial_capital,
        cash_ratio=args.cash_ratio,
        stock_ratio=args.stock_ratio,
        rebalance_threshold=args.rebalance_threshold,
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
    base_filename = f"rebalance_report_{stock_code}_cash{args.cash_ratio}_stock{args.stock_ratio}_threshold{args.rebalance_threshold}"
    if args.start_date:
        base_filename += f"_start{args.start_date.replace('-', '')}"
    
    # 開啟報告檔案
    report_filename = os.path.join(output_dir, base_filename + ".txt")
    with open(report_filename, 'w', encoding='utf-8') as f:
        # 寫入參數設定
        f.write("=== 參數設定 ===\n")
        f.write(f"股票資料: {args.data_file}\n")
        f.write(f"初始資金: {args.initial_capital:,.2f}\n")
        f.write(f"現金比例: {args.cash_ratio}\n")
        f.write(f"股票比例: {args.stock_ratio}\n")
        f.write(f"再平衡閾值: {args.rebalance_threshold}\n")
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
        
        # 寫入最終資產配置
        final_portfolio = strategy.portfolio_value[-1]
        f.write("=== 最終資產配置 ===\n")
        f.write(f"持股價值: {final_portfolio['stocks']:,.2f}\n")
        f.write(f"現金量: {final_portfolio['cash']:,.2f}\n")
        f.write(f"總資產: {final_portfolio['total_value']:,.2f}\n")
        f.write(f"持股比例: {(final_portfolio['stocks'] / final_portfolio['total_value'] * 100):.2f}%\n")
        f.write(f"現金比例: {(final_portfolio['cash'] / final_portfolio['total_value'] * 100):.2f}%\n")
    
    # 繪製圖表
    chart_filename = strategy.plot_results(
        args.data_file,
        args.cash_ratio,
        args.stock_ratio,
        args.rebalance_threshold,
        args.start_date
    )
    
    # 輸出到終端機
    print(f"\n報告已儲存為 {report_filename}")
    print(f"圖表已儲存為 {chart_filename}")
    
    # 同時在終端機顯示最終資產配置
    print("\n=== 最終資產配置 ===")
    print(f"持股價值: {final_portfolio['stocks']:,.2f}")
    print(f"現金量: {final_portfolio['cash']:,.2f}")
    print(f"總資產: {final_portfolio['total_value']:,.2f}")
    print(f"持股比例: {(final_portfolio['stocks'] / final_portfolio['total_value'] * 100):.2f}%")
    print(f"現金比例: {(final_portfolio['cash'] / final_portfolio['total_value'] * 100):.2f}%")

if __name__ == "__main__":
    main() 