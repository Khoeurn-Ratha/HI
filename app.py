from datetime import date, datetime
import os
from typing import Optional
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from jinja2 import Template
from sqlmodel import Field, SQLModel, Session, create_engine, select

# --- 1. CSS Style (Glassmorphism & Fresh Animated Background) ---
CSS_STYLE = """
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes backgroundFlow {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

:root {
  --bg-dark: #07090e;
  --panel-bg: rgba(17, 24, 39, 0.75);
  --border-color: rgba(255, 255, 255, 0.08);
  --accent: #f59e0b;
  --accent-light: #fbbf24;
  --text-main: #f9fafb;
  --text-muted: #9ca3af;
  --gain: #10b981;
  --loss: #ef4444;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  min-height: 100vh;
  color: var(--text-main);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  line-height: 1.5;
  background: linear-gradient(-45deg, #07090e, #111827, #1f130b, #090d16);
  background-size: 400% 400%;
  animation: backgroundFlow 15s ease infinite;
}

.page {
  max-width: 680px;
  margin: 0 auto;
  padding: 48px 24px 80px;
  animation: fadeIn 0.6s ease-out;
}

.masthead { text-align: center; margin-bottom: 40px; }

.eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.2em;
  font-size: 11px;
  color: var(--accent);
  margin: 0 0 10px;
  font-weight: 700;
}

.masthead h1 {
  font-weight: 700;
  font-size: clamp(32px, 5vw, 42px);
  margin: 0 0 10px;
  color: var(--text-main);
  letter-spacing: -0.01em;
  text-shadow: 0 2px 15px rgba(245, 158, 11, 0.2);
}

.subtitle { color: var(--text-muted); margin: 0; font-size: 14.5px; }

/* Stats Summary Cards */
.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: var(--panel-bg);
  backdrop-filter: blur(12px);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
}

.stat-card.gain-card { border-color: rgba(16, 185, 129, 0.3); }
.stat-card.loss-card { border-color: rgba(239, 68, 68, 0.3); }

.stat-title {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-muted);
  margin-bottom: 8px;
  font-weight: 600;
}

.stat-value {
  font-size: 22px;
  font-weight: 700;
}

.stat-value.gain { color: var(--gain); }
.stat-value.loss { color: var(--loss); }

.panel {
  background: var(--panel-bg);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 28px;
  margin-bottom: 24px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
  transition: border-color 0.3s ease, transform 0.3s ease;
  animation: fadeIn 0.8s ease-out;
}

.panel:hover {
  border-color: rgba(245, 158, 11, 0.4);
  transform: translateY(-2px);
}

.panel h2 {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-color);
  color: var(--accent-light);
  letter-spacing: 0.02em;
}

.rules { list-style: none; margin: 0; padding: 0; }

.rules li {
  display: flex;
  gap: 16px;
  padding: 12px 0;
  border-bottom: 1px solid var(--border-color);
  transition: all 0.2s ease;
}

.rules li:hover {
  transform: translateX(4px);
  color: var(--accent-light);
  background: rgba(245, 158, 11, 0.03);
  padding-left: 6px;
  border-radius: 4px;
}

.rules li:last-child { border-bottom: none; }

.num {
  color: var(--accent);
  font-size: 13px;
  padding-top: 2px;
  flex-shrink: 0;
  width: 22px;
  font-weight: 700;
}

.rule-text { font-size: 14.5px; color: var(--text-main); }
.rule-text strong { color: var(--accent-light); font-weight: 600; }

.flash {
  padding: 14px 18px;
  border-radius: 8px;
  font-size: 14px;
  margin-bottom: 24px;
  border: 1px solid;
  animation: fadeIn 0.4s ease-out;
  backdrop-filter: blur(8px);
}
.flash-gain { background: rgba(16, 185, 129, 0.15); border-color: var(--gain); color: #34d399; }
.flash-loss { background: rgba(239, 68, 68, 0.15); border-color: var(--loss); color: #f87171; }

.entry-form { display: flex; gap: 16px; align-items: flex-end; flex-wrap: wrap; }

.field { display: flex; flex-direction: column; gap: 6px; flex: 1; min-width: 140px; }

.field label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-muted);
  font-weight: 600;
}

.field select, .field input {
  background: rgba(7, 9, 14, 0.6);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 12px 14px;
  color: var(--text-main);
  font-size: 15px;
  width: 100%;
  transition: all 0.2s ease;
}

.field select:focus, .field input:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.2);
  background: rgba(7, 9, 14, 0.9);
}

.stamp {
  background: linear-gradient(135deg, var(--accent), #d97706);
  color: #07090e;
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  font-weight: 700;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3);
  transition: all 0.2s ease;
}

.stamp:hover { 
  filter: brightness(1.1); 
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(245, 158, 11, 0.4);
}
.stamp:active { transform: translateY(1px); box-shadow: none; }

.ledger-table { width: 100%; border-collapse: collapse; font-size: 14px; }

.ledger-table th {
  text-align: left;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-muted);
  padding: 0 0 12px;
  border-bottom: 1px solid var(--border-color);
}

.ledger-table td { padding: 12px 0; border-bottom: 1px solid var(--border-color); }
.ledger-table tr { transition: background 0.15s ease; }
.ledger-table tr:hover td { 
  background: rgba(245, 158, 11, 0.05); 
}
.ledger-table tr:last-child td { border-bottom: none; }

.badge-gain { color: var(--gain); font-weight: 600; }
.badge-loss { color: var(--loss); font-weight: 600; }

.muted { color: var(--text-muted); font-size: 12.5px; }
.empty { color: var(--text-muted); font-size: 14px; margin: 0; text-align: center; padding: 20px 0; }
.foot { text-align: center; color: var(--text-muted); font-size: 12.5px; margin-top: 24px; }
.foot code {
  background: rgba(7, 9, 14, 0.6);
  padding: 3px 8px;
  border-radius: 4px;
  border: 1px solid var(--border-color);
  color: var(--accent-light);
}
"""

# --- 2. HTML Template ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Trade Ledger - Dashboard</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>
{{ css_style | safe }}
</style>
</head>
<body>
<main class="page">

  <header class="masthead">
    <p class="eyebrow">Daily Trade Ledger</p>
    <h1>Rule Before Risk</h1>
    <p class="subtitle">Track your performance, profit, and loss cleanly.</p>
  </header>

  <!-- Total Profit & Loss Summary Cards -->
  <section class="stats-grid">
    <div class="stat-card gain-card">
      <div class="stat-title">Total Profit (Gain)</div>
      <div class="stat-value gain">+${{ "%.2f"|format(total_gain) }}</div>
    </div>
    <div class="stat-card loss-card">
      <div class="stat-title">Total Loss</div>
      <div class="stat-value loss">-${{ "%.2f"|format(total_loss) }}</div>
    </div>
  </section>

  <section class="panel rules-panel" aria-label="Trade rules">
    <h2>The Rules</h2>
    <ol class="rules">
      <li><span class="num">01</span><span class="rule-text"><strong>No FOMO.</strong> Skip anything you didn't plan for.</span></li>
      <li><span class="num">02</span><span class="rule-text"><strong>One signal.</strong> No entries on a different or conflicting signal.</span></li>
      <li><span class="num">03</span><span class="rule-text"><strong>1&ndash;2 setups a day.</strong> That's the ceiling.</span></li>
      <li><span class="num">04</span><span class="rule-text"><strong>Risk : Reward = 1 : 2.</strong> Every trade.</span></li>
      <li><span class="num">05</span><span class="rule-text"><strong>15m &rarr; 1m.</strong> Read flow on the 15m, drop to 1m to enter &mdash; confirm MSS and TS first.</span></li>
      <li><span class="num">06</span><span class="rule-text"><strong>1H key level &rarr; 5m / 3m.</strong> Confirm MSS before entry.</span></li>
      <li><span class="num">07</span><span class="rule-text"><strong>4H key level &rarr; 15m / 5m.</strong> Confirm MSS before entry.</span></li>
      <li><span class="num">08</span><span class="rule-text"><strong>$5&ndash;$10 target, $5 max loss.</strong> Down $5 on the day &mdash; done trading.</span></li>
    </ol>
  </section>

  {% if message %}<div class="flash flash-gain" role="status">{{ message }}</div>{% endif %}
  {% if error %}<div class="flash flash-loss" role="alert">{{ error }}</div>{% endif %}

  <section class="panel entry-panel" aria-label="Log a trade">
    <h2>New Trade Entry</h2>
    <form action="/submit" method="post" class="entry-form">
      <div class="field">
        <label for="date">Date</label>
        <input type="date" id="date" name="date" required>
      </div>
      <div class="field">
        <label for="type">Result Type</label>
        <select id="type" name="type" required>
          <option value="GAIN">🟢 Profit (Gain)</option>
          <option value="LOSS">🔴 Loss</option>
        </select>
      </div>
      <div class="field">
        <label for="amount">Amount ($)</label>
        <input type="number" id="amount" name="amount" step="0.01" inputmode="decimal" placeholder="10.00" required>
      </div>
      <button type="submit" class="stamp">Log Trade</button>
    </form>
  </section>

  <section class="panel log-panel" aria-label="Logged entries">
    <h2>Trade History</h2>
    {% if trades %}
    <table class="ledger-table">
      <thead>
        <tr><th>Date</th><th>Type</th><th>Amount</th><th>Logged At</th></tr>
      </thead>
      <tbody>
        {% for row in trades %}
        <tr>
          <td>{{ row.trade_date }}</td>
          <td>
            {% if row.trade_type == 'GAIN' %}
              <span class="badge-gain">GAIN</span>
            {% else %}
              <span class="badge-loss">LOSS</span>
            {% endif %}
          </td>
          <td>
            {% if row.trade_type == 'GAIN' %}
              <span class="badge-gain">+${{ "%.2f"|format(row.amount) }}</span>
            {% else %}
              <span class="badge-loss">-${{ "%.2f"|format(row.amount) }}</span>
            {% endif %}
          </td>
          <td class="muted">{{ row.logged_at.strftime('%Y-%m-%d %H:%M') if row.logged_at else '' }}</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
    {% else %}
    <p class="empty">Nothing logged yet. Your first trade entry will show up here.</p>
    {% endif %}
  </section>

  <footer class="foot">
    <p>Stored in Database &mdash; viewable via pgAdmin or <code>/admin</code>.</p>
  </footer>

</main>
</body>
</html>
"""

# --- 3. Database Model & Setup ---
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///trading.db")
if DATABASE_URL.startswith("postgres://"):
  DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://ramote_user:KB6MBdQ5zXkT5zDZ5APXNmBAVgUx6SDZ@dpg-da8k9vijnfac73emabgg-a/ramote", 1)

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
    if "sqlite" in DATABASE_URL
    else {}
)


class Trade(SQLModel, table=True):
  id: Optional[int] = Field(default=None, primary_key=True)
  trade_date: date
  trade_type: str  # 'GAIN' ឬ 'LOSS'
  amount: float  # ចំនួនទឹកប្រាក់ ($)
  logged_at: datetime = Field(default_factory=datetime.utcnow)


from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
  SQLModel.metadata.create_all(engine)
  yield


app = FastAPI(lifespan=lifespan)


# --- 4. Routes ---
@app.get("/", response_class=HTMLResponse)
def read_root(message: Optional[str] = None, error: Optional[str] = None):
  with Session(engine) as session:
    trades = session.exec(
        select(Trade).order_by(Trade.logged_at.desc())
    ).all()

    # គណនាសរុប Profit (Gain) និង Total Loss
    total_gain = sum(t.amount for t in trades if t.trade_type == "GAIN")
    total_loss = sum(t.amount for t in trades if t.trade_type == "LOSS")

  template = Template(HTML_TEMPLATE)
  return template.render(
      css_style=CSS_STYLE,
      trades=trades,
      total_gain=total_gain,
      total_loss=total_loss,
      message=message,
      error=error,
  )


@app.post("/submit", response_class=HTMLResponse)
def submit_trade(
    date: date = Form(...),
    type: str = Form(...),
    amount: float = Form(...),
):
  try:
    with Session(engine) as session:
      new_trade = Trade(trade_date=date, trade_type=type, amount=amount)
      session.add(new_trade)
      session.commit()
    return RedirectResponse(
        url="/?message=Trade+logged+successfully!",
        status_code=303,
    )
  except Exception as e:
    return RedirectResponse(
        url=f"/?error=Error+saving+trade:+{str(e)}", status_code=303
    )
