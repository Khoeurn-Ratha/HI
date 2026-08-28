import os
import pandas as pd
from flask import Flask, request, redirect, url_for, render_template_string

app = Flask(__name__)

EXCEL_FILE = 'trading_journal.xlsx'

def init_excel():
    if not os.path.exists(EXCEL_FILE):
        df = pd.DataFrame(columns=['Date', 'Price', 'Notes'])
        df.to_excel(EXCEL_FILE, index=False)

init_excel()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trading Journal & Rules</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #121212; color: #e0e0e0; padding: 20px; }
        .container { max-width: 600px; margin: auto; background: #1e1e1e; padding: 20px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
        h2, h3 { color: #4CAF50; }
        .rules-box { background: #2a2a2a; padding: 15px; border-left: 5px solid #ff9800; margin-bottom: 20px; border-radius: 4px; }
        .rules-box ol { padding-left: 20px; margin: 0; line-height: 1.6; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input[type="date"], input[type="number"], textarea { width: 100%; padding: 10px; box-sizing: border-box; background: #2d2d2d; border: 1px solid #444; color: #fff; border-radius: 4px; }
        button { background-color: #4CAF50; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; width: 100%; }
        button:hover { background-color: #45a049; }
    </style>
</head>
<body>

<div class="container">
    <h2>📊 My Trading Journal & Rules</h2>

    <div class="rules-box">
        <h3>📌 Trading Rules (ក្បួនច្បាប់เทรឌ)</h3>
        <ol>
            <li>Don't FOMO</li>
            <li>Don't entry with another signal</li>
            <li>One day one setup or 2 setup</li>
            <li>Risk 1:2 RR</li>
            <li>Use TF 15m look flow chart and 1m entry (If want entry look MSS and TS)</li>
            <li>Use 1H key level, entry 5m and 3m (Looking MSS first)</li>
            <li>Use 4H key level, entry 15m and 5m (Looking MSS first)</li>
            <li>One day target $5 or $10, risk $5. If losing $5, stop trade!</li>
        </ol>
    </div>

    <form action="/submit" method="POST">
        <div class="form-group">
            <label for="date">Select Date:</label>
            <input type="date" id="date" name="date" required>
        </div>

        <div class="form-group">
            <label for="price">Input Price ($):</label>
            <input type="number" step="any" id="price" name="price" placeholder="Enter entry price" required>
        </div>

        <div class="form-group">
            <label for="notes">Notes / Strategy:</label>
            <textarea id="notes" name="notes" rows="3" placeholder="e.g., 1H Key Level, MSS confirmed"></textarea>
        </div>

        <button type="submit">Submit Trade</button>
    </form>
</div>

</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/submit', methods=['POST'])
def submit():
    trade_date = request.form.get('date')
    trade_price = request.form.get('price')
    trade_notes = request.form.get('notes', '')

    df = pd.read_excel(EXCEL_FILE)
    new_data = pd.DataFrame({'Date': [trade_date], 'Price': [trade_price], 'Notes': [trade_notes]})
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False)

    return redirect(url_for('index'))

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)