import os
from openai import OpenAI
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
def initialize_openai():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning("OpenAI API key not found in environment variables")
        return None
    return OpenAI(api_key=api_key)

def get_trading_opinion(option_chain_data):
    """
    Generate trading opinion using OpenAI based on option chain data
    """
    try:
        if option_chain_data is None or option_chain_data.empty:
            raise ValueError("No option chain data available")

        client = initialize_openai()
        if client is None:
            return {
                "recommendation": "AI analysis unavailable - API key not configured",
                "confidence": 0,
                "direction": "NEUTRAL",
                "key_factors": ["API configuration required"],
                "timestamp": datetime.now().isoformat()
            }

        # Prepare data for AI analysis
        market_data = {
            "pcr": float(option_chain_data['PCR'].mean()),
            "max_pain": float(option_chain_data['MaxPain'].mean()),
            "spot_price": float(option_chain_data['SpotPrice'].mean()),
            "total_ce_oi": int(option_chain_data['CE_OI'].sum()),
            "total_pe_oi": int(option_chain_data['PE_OI'].sum()),
        }

        prompt = f"""
        Analyze the following Nifty50 options data and provide a trading recommendation:

        Put-Call Ratio: {market_data['pcr']}
        Max Pain: {market_data['max_pain']}
        Current Price: {market_data['spot_price']}
        Total CE OI: {market_data['total_ce_oi']}
        Total PE OI: {market_data['total_pe_oi']}

        Provide the analysis in JSON format with the following structure:
        {{
            "recommendation": "detailed trading recommendation",
            "confidence": "confidence score between 0 and 1",
            "direction": "BULLISH/BEARISH/NEUTRAL",
            "key_factors": ["list of key factors considered"]
        }}
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert options trading analyst."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )

        analysis = json.loads(response.choices[0].message.content)
        analysis['timestamp'] = datetime.now().isoformat()
        return analysis

    except Exception as e:
        logger.error(f"Failed to generate trading opinion: {str(e)}")
        return {
            "recommendation": f"Error generating trading opinion: {str(e)}",
            "confidence": 0,
            "direction": "NEUTRAL",
            "key_factors": ["Error occurred during analysis"],
            "timestamp": datetime.now().isoformat()
        }