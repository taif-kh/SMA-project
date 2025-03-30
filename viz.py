from mesa.visualization.modules import ChartModule, CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from stock_market_model import StockMarket, Investor, Company
import random

def agent_portrayal(agent):
    """Define how agents appear in the visualization."""
    if isinstance(agent, Company):
        if len(agent.price_history) > 1:
            color = "green" if agent.price_history[-1] > agent.price_history[-2] else "red" if agent.price_history[-1] < agent.price_history[-2] else "blue"
        else:
            color = "blue"

        return {"Shape": "rect", "Color": color, "Filled": "true", "Layer": 0, "w": 0.8, "h": 0.8}

    elif isinstance(agent, Investor):
        return {"Shape": "circle", "Color": "green", "Filled": "true", "Layer": 1, "r": 0.5}

# Set up grid visualization
grid = CanvasGrid(agent_portrayal, 10, 10, 500, 500)

# Add a stock price chart for each company
price_chart = ChartModule(
    [{"Label": f"Company {i}", "Color": random.choice(["blue", "red", "green"])} for i in range(3)],
    data_collector_name="datacollector"
)

# Add a chart for investor cash holdings
cash_chart = ChartModule([{"Label": "Cash", "Color": "green"}], data_collector_name="datacollector")

# Create the server with interactive parameters
server = ModularServer(
    StockMarket,
    [grid, price_chart, cash_chart],
    "Stock Market Simulation",
    {
        "num_companies": UserSettableParameter("slider", "Number of Companies", 3, 1, 10, 1),
        "num_investors": UserSettableParameter("slider", "Number of Investors", 5, 1, 20, 1),
        "volatility": UserSettableParameter("slider", "Market Volatility", 0.05, 0.01, 0.1, 0.01),
        "initial_cash": UserSettableParameter("slider", "Initial Cash per Investor", 1000, 500, 5000, 100),
    }
)

server.port = 8521  # Default Mesa port
server.launch()
