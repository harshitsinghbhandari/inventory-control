import simpy
import random
import statistics
import logging
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

logger = logging.getLogger("InventoryLogger")
logger.setLevel(logging.INFO)

formatter = logging.Formatter("[%(asctime)s][DAY %(day)d] %(message)s", "%H:%M:%S")

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)


file_handler = logging.FileHandler('inventory.log', mode='w')
file_handler.setFormatter(formatter)


logger.addHandler(console_handler)
logger.addHandler(file_handler)

def log_normal_lead_time_generator(mu: float, sigma: float):
    """
    Infinite generator yielding lead times following a log-normal distribution.
    
    Parameters:
    - mu: mean of the underlying normal distribution (log scale)
    - sigma: standard deviation of the underlying normal distribution (log scale)
    
    Yields:
    - A single random sample of lead time each time next() is called
    """
    while True:
        lead_time = np.random.lognormal(mean=mu, sigma=sigma)
        yield lead_time

def ar1_demand_generator(phi=0.8, mu=0, sigma=8, base_demand=20, min_demand=0):
    """
    Returns a generator that simulates AR(1) demand over time.
    
    - phi: autocorrelation coefficient
    - mu, sigma: parameters for noise
    - base_demand: long-run mean demand level
    - min_demand: minimum demand allowed (e.g., 0)
    """
    prev_demand = base_demand  # Initialize at mean demand

    while True:
        noise = random.normalvariate(mu, sigma)
        new_demand = phi * prev_demand + (1 - phi) * base_demand + noise
        new_demand = max(min_demand, int(round(new_demand)))
        prev_demand = new_demand
        yield new_demand
import random

def lumpy_ar1_demand_generator(
    phi=0.8,
    mu=0,
    sigma=8,
    base_demand=20,
    min_demand=0,
    p_occurrence=0.8  # Probability that demand occurs in a time period
):
    """
    Generator that simulates lumpy (intermittent) demand using an AR(1) process.
    
    - phi: AR(1) autocorrelation coefficient
    - mu, sigma: noise parameters for AR(1)
    - base_demand: long-run mean demand level
    - min_demand: minimum possible demand (e.g., 0)
    - p_occurrence: probability that demand occurs in a given time period
    """
    prev_demand = base_demand

    while True:
        # Step 1: Determine if demand occurs
        if random.random() < p_occurrence:
            # Step 2: Generate demand using AR(1)
            noise = random.normalvariate(mu, sigma)
            new_demand = phi * prev_demand + (1 - phi) * base_demand + noise
            new_demand = max(min_demand, int(round(new_demand)))
            prev_demand = new_demand
        else:
            new_demand = 0  # No demand this period

        yield new_demand

class DayFilter(logging.Filter):
    def __init__(self):
        super().__init__()
        self.current_day = 0

    def filter(self, record):
        record.day = self.current_day
        return True

day_filter = DayFilter()
logger.addFilter(day_filter)



class InventorySystem:
    def __init__(self, env, s, S, order_cost, holding_cost, simulation_time, verbose=True):
        self.env = env
        self.s = s
        self.S = S
        self.order_cost = order_cost
        self.holding_cost = holding_cost
        self.simulation_time = simulation_time
        self.verbose = verbose
        self.demand_gen = lumpy_ar1_demand_generator()
        self.lead_time_gen = log_normal_lead_time_generator(mu=0, sigma=1)  
        # State
        self.inventory_level = S
        self.order_limit = 2*S

        # KPIs
        self.total_demand = 0
        self.total_fulfilled = 0
        self.stockouts = 0
        self.inventory_levels = []
        self.orders={}
        self.order_received = []
        self.lost_sales = []
        self.total_ordering_cost = 0
        self.total_holding_cost = 0
        
        # Start processes
        self.env.process(self.customer_demand())
        self.env.process(self.inventory_monitor())

    def log(self, msg):
        if self.verbose:
            day_filter.current_day = int(self.env.now)
            logger.info(msg)
    
    def get_demand(self):
        return next(self.demand_gen)
    def lead_time_func(self):
        return int(next(self.lead_time_gen))


    def customer_demand(self):
        while True:
            yield self.env.timeout(1)
            demand = self.get_demand()
            self.total_demand += demand

            if self.inventory_level >= demand:
                self.inventory_level -= demand
                self.total_fulfilled += demand
                self.log(f"Demand: {demand}, Fulfilled: {demand}, Inventory: {self.inventory_level}")
            else:
                self.total_fulfilled += self.inventory_level
                self.log(f"Stockout! Demand: {demand}, Fulfilled: {self.inventory_level}, Inventory: 0")
                self.lost_sales.append(demand - self.inventory_level)
                self.stockouts += 1
                self.inventory_level = 0

            self.inventory_levels.append(self.inventory_level)
            self.total_holding_cost += self.inventory_level * self.holding_cost

    def inventory_monitor(self):
        while True:
            yield self.env.timeout(1)
            if self.inventory_level < self.s and sum(list(self.orders.values())) - sum(self.order_received) < self.order_limit:
                order_qty = self.S - self.inventory_level
                self.total_ordering_cost += self.order_cost
                self.orders[self.env.now] = order_qty
                self.log(f"Placing order for {order_qty} units (Inventory: {self.inventory_level}, Threshold: {self.s})")
                self.env.process(self.receive_order(order_qty))

    def receive_order(self, amount):
        lead_time = self.lead_time_func()
        self.log(f"Order of {amount} units will arrive in {lead_time} days")
        yield self.env.timeout(lead_time)
        self.inventory_level += amount
        self.log(f"Order of {amount} units received. Inventory: {self.inventory_level}")
        self.order_received.append(amount)

    def get_kpis(self):
        fill_rate = self.total_fulfilled / self.total_demand if self.total_demand else 0
        avg_inventory = statistics.mean(self.inventory_levels)
        return {
            'Fill Rate': round(fill_rate, 4),
            'Stockouts': self.stockouts,
            'Average Inventory Level': round(avg_inventory, 2),
            'Total Ordering Cost': round(self.total_ordering_cost, 2),
            'Total Holding Cost': round(self.total_holding_cost, 2),
            'Total Cost': round(self.total_ordering_cost + self.total_holding_cost, 2)
        }
    def get_data(self):
        return {
            'inventory_levels': self.inventory_levels,
            'orders': self.orders,
            'lost_sales': self.lost_sales
        }   

def run_simulation(s=20, S=100, sim_time=365, seed=42, verbose=True):
    random.seed(seed)

    order_cost = 50
    holding_cost = 1

    env = simpy.Environment()
    system = InventorySystem(env, s, S, order_cost, holding_cost, sim_time, verbose=verbose)
    env.run(until=sim_time)

    kpis = system.get_kpis()
    # print("\n=== Simulation KPIs ===")
    # print(kpis)
    # for k, v in kpis.items():
    #     print(f"{k}: {v}")
    return kpis, system.get_data()
def plot_inventory_levels(inventory_data):
    plt.figure(figsize=(12, 6))
    plt.plot(inventory_data['inventory_levels'], label='Inventory Level', color='blue', marker='o', markersize=2)
    plt.title('Inventory Levels Over Time')
    plt.xlabel('Days')
    plt.ylabel('Inventory Level')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    kpis,data=run_simulation(s=20,S=100)
    print("\n=== Simulation KPIs ===")
    for k, v in kpis.items():
        print(f"{k}: {v}")
    plot_inventory_levels(data)
