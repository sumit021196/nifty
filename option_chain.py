import pandas as pd
from nsepython import nse_optionchain_scrapper
import logging
import time
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_option_chain(max_retries=3, retry_delay=5):
    """
    Fetches the Nifty50 option chain data from NSE with retry mechanism
    Returns a processed DataFrame
    """
    for attempt in range(max_retries):
        try:
            logger.info(f"Fetching option chain data - attempt {attempt + 1}/{max_retries}")

            # Fetch option chain data
            option_chain = nse_optionchain_scrapper("NIFTY")

            if not option_chain:
                raise Exception("Failed to fetch option chain data - empty response")

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

            # Calculate Max Pain - Fixed calculation
            spot_price = option_chain['records']['underlyingValue']
            df['CE_Pain'] = df['CE_OI'] * abs(df['Strike'] - spot_price)
            df['PE_Pain'] = df['PE_OI'] * abs(df['Strike'] - spot_price)
            df['Total_Pain'] = df['CE_Pain'] + df['PE_Pain']
            max_pain_strike = df.loc[df['Total_Pain'].idxmin(), 'Strike']
            df['MaxPain'] = max_pain_strike

            # Add spot price
            df['SpotPrice'] = spot_price

            logger.info("Successfully fetched and processed option chain data")
            return df

        except Exception as e:
            logger.error(f"Error fetching option chain data (attempt {attempt + 1}): {str(e)}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("Max retries reached, raising exception")
                raise