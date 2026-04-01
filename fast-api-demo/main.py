import os
from fastapi import FastAPI
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
# typically we would save these credentials in your .env file for security
url = os.getenv("Supabase_URL")
key = os.getenv("SupabaseAPI")

app = FastAPI()
supabase = create_client(url, key)

@app.get("/report/{symbol}")
async def analyze_stock(symbol: str):
    # 1. Fetch the data from Supabase
    response = supabase.table("stock_records") \
        .select("*") \
        .eq("ticker", symbol.upper()) \
        .order("created_at", desc=True) \
        .limit(1) \
        .execute()

    if not response.data:
        return {"error": "No data found in database. Run ingest.py first."}

    record = response.data[0]
    initial_p = record['initial_price']
    final_p = record['final_price']

    # 2. TASK: Determine the Signal
    # Logic: If final > initial, signal is "Bullish". Otherwise "Bearish".
    # YOUR CODE HERE
    signal = "Bullish" if final_p > initial_p else "Bearish"

    return {
        "ticker": symbol.upper(),
        "analysis": {
            "start_price": initial_p,
            "current_price": final_p,
            "signal": signal,
            "source": "Internal Database"
        }
    }
