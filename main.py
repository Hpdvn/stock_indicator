import M5
from M5 import *
import requests2
import json
import time

headers = {
    'x-rapidapi-key': "YOUR_API_KEY",
    'x-rapidapi-host': "yahoo-finance15.p.rapidapi.com"
}

# tickers you would like to follow
tickers_list = [
    'AAPL',
    'RACE',
    'TTE'
]

class InfiniteLooper:
    def __init__(self, items):
        self.items = items
        self.index = -1

    def next(self):
        if not self.items:
            return None
        self.index = (self.index + 1) % len(self.items)
        return self.items[self.index]

looper = InfiniteLooper(tickers_list)

def setup():
    M5.begin()
    M5.Lcd.setRotation(1)
    M5.Lcd.fillScreen(0x000000)

def show_loader():
    max_dollars = 3
    screen_width = M5.Lcd.width()
    screen_height = M5.Lcd.height()

    for i in range(10):
        count = (i % max_dollars) + 1
        loader_str = "$" * count
        text_width = len(loader_str) * 30
        x_position = (screen_width - text_width) // 2
        y_position = (screen_height // 2) - 30

        M5.Lcd.fillScreen(0x000000)
        M5.Lcd.setCursor(x_position, y_position)
        M5.Lcd.setTextSize(5)
        M5.Lcd.setTextColor(0xFFFF00)
        M5.Lcd.print(loader_str)
        time.sleep(0.2)
        M5.update()

def truncate_text(text, max_length):
    if len(text) > max_length:
        return text[:max_length]
    return text

def display_ticker_info(ticker):
    show_loader()
    url = f"https://yahoo-finance15.p.rapidapi.com/api/v1/markets/quote?ticker={ticker}&type=STOCKS"

    try:
        response = requests2.get(url, headers=headers)
        data = response.text
        print(data)
        parsed = json.loads(data)
        body = parsed.get('body', {})
        symbol = body.get('symbol', 'Unknown')
        company = body.get('companyName', 'N/A')
        last_price = body.get('primaryData', {}).get('lastSalePrice', 'N/A')
        net_change = body.get('primaryData', {}).get('netChange', 'N/A')
        pct_change = body.get('primaryData', {}).get('percentageChange', 'N/A')
        week_range = body.get('keyStats', {}).get('fiftyTwoWeekHighLow', {}).get('value', 'N/A')

        # Convert net_change to a float
        try:
            net_change = float(net_change)
        except ValueError:
            net_change = 0.0

        M5.Lcd.fillScreen(0x000000)

        # Display symbol and truncated company name
        M5.Lcd.setTextSize(2)
        M5.Lcd.setTextColor(0xFFFFFF)
        max_length = 12  # Define the maximum length for the company name
        truncated_company = truncate_text(company, max_length)
        M5.Lcd.setCursor(0, 10)
        M5.Lcd.print(f"{symbol} - {truncated_company}")

        # Center the price
        M5.Lcd.setTextSize(3)
        price_str = f"{last_price}"
        price_width = len(price_str) * 18
        x_position_price = (M5.Lcd.width() - price_width) // 2
        M5.Lcd.setCursor(x_position_price, 40)
        M5.Lcd.print(price_str)

        # Center the price difference with color coding
        M5.Lcd.setTextSize(2)
        diff_str = f"{net_change} ({pct_change})"
        diff_width = len(diff_str) * 12
        x_position_diff = (M5.Lcd.width() - diff_width) // 2

        if net_change > 0:
            M5.Lcd.setTextColor(0x00FF00)  # Green for positive
        elif net_change < 0:
            M5.Lcd.setTextColor(0xFF0000)  # Red for negative
        else:
            M5.Lcd.setTextColor(0xFFFFFF)  # White for neutral

        M5.Lcd.setCursor(x_position_diff, 80)
        M5.Lcd.print(diff_str)

        # Center the 52-week range
        M5.Lcd.setTextColor(0xFFFFFF)
        range_str = f"{week_range}"
        range_width = len(range_str) * 12
        x_position_range = (M5.Lcd.width() - range_width) // 2
        M5.Lcd.setCursor(x_position_range, 110)
        M5.Lcd.print(range_str)

        response.close()
    except Exception as e:
        print("Erreur HTTP ou parsing:", e)
        M5.Lcd.fillScreen(0x000000)
        M5.Lcd.setCursor(0, 0)
        M5.Lcd.print("Erreur réseau")

def loop():
    M5.update()
    if M5.BtnA.wasPressed():
        ticker = looper.next()
        display_ticker_info(ticker)

if __name__ == '__main__':
    setup()
    display_ticker_info(looper.next())
    while True:
        loop()
        time.sleep(0.1)
