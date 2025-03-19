import pandas as pd
from nsepython import nse_optionchain_scrapper
import logging

def fetch_option_chain():
    """
    Fetches the Nifty50 option chain data from NSE
    Returns a processed DataFrame
    """
    try:
        # Fetch option chain data
        option_chain = nse_optionchain_scrapper("NIFTY")
        
        if not option_chain:
            raise Exception("Failed to fetch option chain data")
        
        # Extract relevant data
        records = []
        
        for strike in option_chain['records']['data']:
            if 'CE' in strike and 'PE' in strike:
                record = {
                    'Strike': strike['strikePrice'],
                    'CE_OI': strike['CE']['openInterest'],
                    'CE_Volume': strike['CE']['totalTradedVolume'],
                    'CE_LTP': strike['CE']['lastPrice'],
                    'PE_OI': strike['PE']['openInterest'],
                    'PE_Volume': strike['PE']['totalTradedVolume'],
                    'PE_LTP': strike['PE']['lastPrice']
                }
                records.append(record)
        
        df = pd.DataFrame(records)
        
        # Calculate additional metrics
        total_ce_oi = df['CE_OI'].sum()
        total_pe_oi = df['PE_OI'].sum()
        df['PCR'] = total_pe_oi / total_ce_oi if total_ce_oi > 0 else 0
        
        # Calculate Max Pain
        df['CE_Pain'] = df['CE_OI'] * abs(df['Strike'] - option_chain['records']['underlyingValue'])
        df['PE_Pain'] = df['PE_OI'] * abs(df['Strike'] - option_chain['records']['underlyingValue'])
        max_pain_strike = df.loc[df['CE_Pain'] + df['PE_Pain'].idxmin(), 'Strike']
        df['MaxPain'] = max_pain_strike
        
        # Add spot price
        df['SpotPrice'] = option_chain['records']['underlyingValue']
        
        return df
        
    except Exception as e:
        logging.error(f"Error fetching option chain data: {str(e)}")
        raise
