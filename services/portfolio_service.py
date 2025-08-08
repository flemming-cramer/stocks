from datetime import datetime
import pandas as pd

def update_portfolio(transaction_data: dict) -> dict:
    """Update the portfolio with a new transaction."""
    transaction_data = transaction_data.copy()
    transaction_data['timestamp'] = pd.Timestamp.now()  # Changed from datetime.now()
    
    # Validate required fields
    required_fields = ['ticker', 'shares', 'price']
    if not all(field in transaction_data for field in required_fields):
        raise ValueError(f"Missing required fields: {required_fields}")
        
    return transaction_data