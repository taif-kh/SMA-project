import random
from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from mesa.time import RandomActivation

class Company(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.stock_price = random.uniform(50, 200)
        self.price_history = [self.stock_price]
        self.pos = (random.randint(0, 9), random.randint(0, 9))  # Random position

    def step(self):
        """Update stock price based on market volatility."""
        change = random.uniform(-self.model.volatility, self.model.volatility) * self.stock_price
        self.stock_price = max(1, self.stock_price + change)  # Prevent negative price
        self.price_history.append(self.stock_price)

class Investor(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.cash = model.initial_cash
        self.pos = (random.randint(0, 9), random.randint(0, 9))  # Start at a random position

    def step(self):
        """Move towards a company and potentially trade."""
        if self.model.companies:
            target_company = random.choice(self.model.companies)

            # Move closer to the company
            new_x = self.pos[0] + (1 if self.pos[0] < target_company.pos[0] else -1 if self.pos[0] > target_company.pos[0] else 0)
            new_y = self.pos[1] + (1 if self.pos[1] < target_company.pos[1] else -1 if self.pos[1] > target_company.pos[1] else 0)

            self.model.grid.move_agent(self, (new_x, new_y))

class StockMarket(Model):
    def __init__(self, num_companies=3, num_investors=5, volatility=0.05, initial_cash=1000):
        self.num_companies = num_companies
        self.num_investors = num_investors
        self.volatility = volatility
        self.initial_cash = initial_cash

        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(10, 10, torus=False)
        
        # Create companies
        self.companies = []
        for i in range(num_companies):
            company = Company(i, self)
            self.schedule.add(company)
            self.grid.place_agent(company, company.pos)
            self.companies.append(company)

        # Create investors
        for i in range(num_investors):
            investor = Investor(i + num_companies, self)
            self.schedule.add(investor)
            self.grid.place_agent(investor, investor.pos)

        self.datacollector = DataCollector(
            {
                "Cash": lambda m: sum(a.cash for a in m.schedule.agents if isinstance(a, Investor)),
                **{f"Company {i}": (lambda m, i=i: m.companies[i].stock_price) for i in range(num_companies)}
            }
        )

        self.running = True  # Enables user interactions

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
