import random
import matplotlib.pyplot as plt
from flask import Flask, render_template, Response
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

class Company:
    def __init__(self, id: int, initial_price: float):
        self.id = id
        self.price = initial_price
        self.price_history = [initial_price]

    def update_price(self, change_factor: float):
        self.price *= change_factor
        self.price = round(self.price, 2)
        self.price_history.append(self.price)

class Investor:
    def __init__(self, id: int, cash: float):
        self.id = id
        self.cash = cash
        self.portfolio = {}  # {company_id: shares}

    def buy_shares(self, company, shares=1):
        cost = shares * company.price
        if self.cash >= cost:
            self.cash -= cost
            self.portfolio[company.id] = self.portfolio.get(company.id, 0) + shares
            company.price *= 1.01  # Price increase due to demand

class StockMarket:
    def __init__(self, n_companies=3, n_investors=5, days=20):
        self.days = days
        self.companies = [Company(i, random.randint(50, 150)) for i in range(n_companies)]
        self.investors = [Investor(i, 1000) for i in range(n_investors)]

    def run_simulation(self):
        for _ in range(self.days):
            for company in self.companies:
                change = 1 + random.uniform(-0.05, 0.05)
                company.update_price(change)

            for investor in self.investors:
                company = random.choice(self.companies)
                investor.buy_shares(company)

app = Flask(__name__)
market = StockMarket()
market.run_simulation()

def generate_plot(fig):
    """Convert Matplotlib figure to PNG"""
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype="image/png")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/plot/stock_prices.png")
def plot_stock_prices():
    fig, ax = plt.subplots(figsize=(6, 4))
    for company in market.companies:
        ax.plot(company.price_history, marker='o', linestyle='-', label=f'Company {company.id}')
    
    ax.set_xlabel("Days")
    ax.set_ylabel("Stock Price")
    ax.set_title("Stock Prices Over Time")
    ax.legend()
    return generate_plot(fig)

@app.route("/plot/investor_cash.png")
def plot_investor_cash():
    fig, ax = plt.subplots(figsize=(6, 4))
    investor_ids = [investor.id for investor in market.investors]
    cash_holdings = [investor.cash for investor in market.investors]

    ax.bar(investor_ids, cash_holdings, color='blue')
    ax.set_xlabel("Investor ID")
    ax.set_ylabel("Cash ($)")
    ax.set_title("Investor Cash Holdings")
    return generate_plot(fig)

@app.route("/plot/investor_shares.png")
def plot_investor_shares():
    fig, ax = plt.subplots(figsize=(6, 4))
    investor_ids = [investor.id for investor in market.investors]
    total_shares = [sum(investor.portfolio.values()) for investor in market.investors]

    ax.bar(investor_ids, total_shares, color='green')
    ax.set_xlabel("Investor ID")
    ax.set_ylabel("Total Shares Owned")
    ax.set_title("Investor Share Holdings")
    return generate_plot(fig)

if __name__ == "__main__":
    app.run(debug=True)
