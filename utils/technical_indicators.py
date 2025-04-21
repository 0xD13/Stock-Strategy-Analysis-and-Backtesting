import pandas as pd
import os # Import os for path manipulation
import numpy as np

def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate the Relative Strength Index (RSI) for a given price series.

    Args:
        prices (pd.Series): Series of prices (typically closing prices).
        period (int): The lookback period for RSI calculation (default: 14).

    Returns:
        pd.Series: Series containing RSI values rounded to 2 decimal places.
    """
    # Calculate price changes
    delta = prices.diff()

    # Separate gains and losses
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    # Calculate average gain and loss over the specified period
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    # Calculate relative strength (RS)
    rs = avg_gain / avg_loss

    # Calculate RSI
    rsi = 100 - (100 / (1 + rs))
    
    # Round to 2 decimal places
    return rsi.round(2)

def analyze_rsi_from_csv(file_path: str, rsi_period: int = 14, tail_rows: int = 100):
    """
    Reads a CSV file, calculates RSI for the closing price, and prints the tail end.

    Args:
        file_path (str): Path to the CSV file.
        rsi_period (int): The period for RSI calculation (default: 14).
        tail_rows (int): Number of trailing rows to print (default: 10).
    """
    try:
        if not os.path.exists(file_path):
             raise FileNotFoundError(f"Data file not found at {file_path}")

        df = pd.read_csv(file_path, index_col='Date', parse_dates=True)
        
        # Identify the closing price column
        close_column = None
        possible_columns = ['Close', 'Adj Close', '收盤價']
        for col in possible_columns:
            if col in df.columns:
                close_column = col
                break
        
        if close_column is None:
            raise ValueError(f"Could not find a closing price column ({', '.join(possible_columns)}) in {file_path}.")

        # Rename if necessary for consistency (optional)
        if close_column != 'Close':
             df.rename(columns={close_column: 'Close'}, inplace=True)
             close_column = 'Close' # Update the variable after renaming

        # Calculate RSI using the identified column
        df['RSI'] = calculate_rsi(df[close_column], period=rsi_period)

        print(f"RSI (period={rsi_period}) calculated for {file_path}. Showing the last {tail_rows} results:")
        # Display the specified number of tail rows, including the RSI
        print(df.tail(tail_rows))

    except FileNotFoundError as fnf:
        print(f"Error: {fnf}")
    except ValueError as ve:
        print(f"Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred while processing {file_path}: {e}")


if __name__ == "__main__":
    # Example usage: Analyze RSI for ^TWII.csv
    # Assuming the script is run from the project root or the path is relative to it
    data_file = 'data/twse/^TWII.csv' 
    analyze_rsi_from_csv(data_file)

    # You could call it for other files too, e.g.:
    # analyze_rsi_from_csv('data/twse/0050.csv', rsi_period=20, tail_rows=5) 