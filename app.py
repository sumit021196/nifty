import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time
from option_chain import fetch_option_chain
from ai_analysis import get_trading_opinion
from data_store import save_opinion, get_historical_opinions
import traceback

st.set_page_config(page_title="Nifty50 Option Chain Analysis", layout="wide")

def create_option_chain_table(df):
    if df is None or df.empty:
        return None

    fig = go.Figure(data=[go.Table(
        header=dict(values=list(df.columns),
                   fill_color='paleturquoise',
                   align='left'),
        cells=dict(values=[df[col] for col in df.columns],
                   fill_color='lavender',
                   align='left'))
    ])
    return fig

def display_metrics(df):
    if df is None or df.empty:
        return

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Put-Call Ratio", f"{df['PCR'].mean():.2f}")
    with col2:
        st.metric("Max Pain", f"{df['MaxPain'].mean():.2f}")
    with col3:
        st.metric("Current Price", f"{df['SpotPrice'].mean():.2f}")

def display_strategy(strategy):
    if "type" in strategy and strategy["type"] == "IRON CONDOR":
        st.markdown(f"""
        **Strategy: {strategy['type']} ({strategy['action']})**
        - Sell Put @ {strategy['strikes']['sell_put']}
        - Buy Put @ {strategy['strikes']['buy_put']}
        - Sell Call @ {strategy['strikes']['sell_call']}
        - Buy Call @ {strategy['strikes']['buy_call']}
        - Target: {strategy['target']}
        - Stop Loss: {strategy['stop_loss']}
        - Rationale: {strategy['rationale']}
        """)
    else:
        st.markdown(f"""
        **Strategy: {strategy['type']} {strategy['action']}**
        - Strike: {strategy['strike']}
        - Target: {strategy['target']}
        - Stop Loss: {strategy['stop_loss']}
        - Rationale: {strategy['rationale']}
        """)

def main():
    st.title("Nifty50 Option Chain Analysis")

    if 'last_update' not in st.session_state:
        st.session_state.last_update = None

    # Refresh data every 5 minutes
    current_time = datetime.now()
    if (st.session_state.last_update is None or 
        (current_time - st.session_state.last_update).seconds >= 300):

        with st.spinner("Fetching latest option chain data..."):
            try:
                option_chain_data = fetch_option_chain()
                if option_chain_data is not None:
                    st.session_state.option_chain_data = option_chain_data
                    st.session_state.last_update = current_time

                    # Get AI trading opinion
                    opinion = get_trading_opinion(option_chain_data)
                    if opinion:
                        save_opinion(opinion)
                        st.session_state.latest_opinion = opinion
            except Exception as e:
                st.error(f"Error fetching data: {str(e)}")
                st.code(traceback.format_exc())
                return

    # Display latest update time
    if st.session_state.last_update:
        st.info(f"Last updated: {st.session_state.last_update.strftime('%Y-%m-%d %H:%M:%S')}")

    # Display option chain data
    if hasattr(st.session_state, 'option_chain_data'):
        display_metrics(st.session_state.option_chain_data)

        fig = create_option_chain_table(st.session_state.option_chain_data)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

    # Display latest AI opinion
    if hasattr(st.session_state, 'latest_opinion'):
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("Market Analysis")
            st.write(st.session_state.latest_opinion['recommendation'])
            st.write(f"Confidence: {st.session_state.latest_opinion['confidence']:.2%}")
            st.write("Key Factors:")
            for factor in st.session_state.latest_opinion['key_factors']:
                st.write(f"• {factor}")

        with col2:
            st.subheader("Suggested Strategies")
            if 'suggested_strategies' in st.session_state.latest_opinion:
                for strategy in st.session_state.latest_opinion['suggested_strategies']:
                    display_strategy(strategy)
                st.caption("Note: These are suggestions only. Please do your own research before trading.")

    # Display historical opinions
    st.subheader("Historical Trading Opinions")
    historical_opinions = get_historical_opinions()
    if historical_opinions:
        opinions_df = pd.DataFrame(historical_opinions)
        st.dataframe(opinions_df)

        # Plot accuracy over time
        if not opinions_df.empty:
            accuracy_fig = go.Figure(data=go.Scatter(
                x=opinions_df['timestamp'],
                y=opinions_df['accuracy'],
                mode='lines+markers'
            ))
            accuracy_fig.update_layout(title="Trading Opinion Accuracy Over Time",
                                     xaxis_title="Date",
                                     yaxis_title="Accuracy")
            st.plotly_chart(accuracy_fig)

if __name__ == "__main__":
    main()