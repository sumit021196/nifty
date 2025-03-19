# Nifty50 Option Chain Analysis Platform

A sophisticated Streamlit-based platform for analyzing Nifty50 option chains, providing AI-powered trading insights and comprehensive market analysis.

## Features

- Real-time Nifty50 option chain data visualization
- Advanced metrics calculation (PCR, Max Pain)
- AI-driven trading strategy recommendations
- Historical trading opinions tracking
- Interactive data visualization with Plotly

## Tech Stack

- Streamlit for web interface
- Python for data processing
- NSE Python for market data
- Plotly for interactive charts
- Render for deployment

## Setup and Installation

1. Clone the repository:
```bash
git clone https://github.com/sumit021196/nifty.git
cd nifty
```

2. Install dependencies:
```bash
pip install -r requirements-render.txt
```

3. Run the application:
```bash
streamlit run app.py
```

## Deployment

The application is configured for deployment on Render platform. Use the following settings:

- Build Command: `pip install -r requirements-render.txt`
- Start Command: `bash start.sh`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
