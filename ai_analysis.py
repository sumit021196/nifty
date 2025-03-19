import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_trading_opinion(option_chain_data):
    """
    Generate trading opinion based on option chain metrics using rule-based analysis
    """
    try:
        if option_chain_data is None or option_chain_data.empty:
            raise ValueError("No option chain data available")

        # Extract key metrics
        pcr = float(option_chain_data['PCR'].mean())
        max_pain = float(option_chain_data['MaxPain'].mean())
        spot_price = float(option_chain_data['SpotPrice'].mean())
        total_ce_oi = int(option_chain_data['CE_OI'].sum())
        total_pe_oi = int(option_chain_data['PE_OI'].sum())

        # Initialize analysis variables
        bullish_factors = []
        bearish_factors = []
        confidence = 0.5  # Base confidence

        # Analyze PCR
        if pcr > 1.5:
            bullish_factors.append("High Put-Call Ratio suggests potential reversal up")
            confidence += 0.1
        elif pcr < 0.7:
            bearish_factors.append("Low Put-Call Ratio suggests potential reversal down")
            confidence += 0.1

        # Analyze Max Pain
        pain_diff = ((max_pain - spot_price) / spot_price) * 100
        if abs(pain_diff) > 0.5:
            if pain_diff > 0:
                bullish_factors.append(f"Price below Max Pain by {pain_diff:.1f}%")
                confidence += 0.1
            else:
                bearish_factors.append(f"Price above Max Pain by {abs(pain_diff):.1f}%")
                confidence += 0.1

        # Analyze OI buildup
        oi_ratio = total_pe_oi / total_ce_oi if total_ce_oi > 0 else 1
        if oi_ratio > 1.2:
            bullish_factors.append("Strong Put writing indicates support")
            confidence += 0.1
        elif oi_ratio < 0.8:
            bearish_factors.append("Strong Call writing indicates resistance")
            confidence += 0.1

        # Determine overall direction
        if len(bullish_factors) > len(bearish_factors):
            direction = "BULLISH"
            key_factors = bullish_factors
            recommendation = "Bullish outlook based on option chain analysis. " + " ".join(bullish_factors)
        elif len(bearish_factors) > len(bullish_factors):
            direction = "BEARISH"
            key_factors = bearish_factors
            recommendation = "Bearish outlook based on option chain analysis. " + " ".join(bearish_factors)
        else:
            direction = "NEUTRAL"
            key_factors = bullish_factors + bearish_factors
            recommendation = "Neutral outlook with mixed signals. Monitor for clearer direction."

        # Cap confidence between 0 and 1
        confidence = min(max(confidence, 0), 1)

        analysis = {
            "recommendation": recommendation,
            "confidence": confidence,
            "direction": direction,
            "key_factors": key_factors,
            "timestamp": datetime.now().isoformat()
        }

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