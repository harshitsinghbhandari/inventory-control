import simpy
import random
import statistics
import logging

logger = logging.getLogger("InventoryLogger")
logger.setLevel(logging.INFO)

formatter = logging.Formatter("[%(asctime)s][DAY %(day)d] %(message)s", "%H:%M:%S")

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)


file_handler = logging.FileHandler("inventory.log", mode='w')
file_handler.setFormatter(formatter)


logger.addHandler(console_handler)
logger.addHandler(file_handler)


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
    def __init__(self, env, s, S, lead_time_func, demand_func, order_cost, holding_cost, simulation_time, verbose=True):
        self.env = env
        self.s = s
        self.S = S
        self.lead_time_func = lead_time_func
        self.demand_func = demand_func
        self.order_cost = order_cost
        self.holding_cost = holding_cost
        self.simulation_time = simulation_time
        self.verbose = verbose

        # State
        self.inventory_level = S

        # KPIs
        self.total_demand = 0
        self.total_fulfilled = 0
        self.stockouts = 0
        self.inventory_levels = []
        self.total_ordering_cost = 0
        self.total_holding_cost = 0

        # Start processes
        self.env.process(self.customer_demand())
        self.env.process(self.inventory_monitor())

    def log(self, msg):
        if self.verbose:
            day_filter.current_day = int(self.env.now)
            logger.info(msg)

    def customer_demand(self):
        while True:
            yield self.env.timeout(1)
            demand = self.demand_func()
            self.total_demand += demand

            if self.inventory_level >= demand:
                self.inventory_level -= demand
                self.total_fulfilled += demand
                self.log(f"Demand: {demand}, Fulfilled: {demand}, Inventory: {self.inventory_level}")
            else:
                self.total_fulfilled += self.inventory_level
                self.log(f"Stockout! Demand: {demand}, Fulfilled: {self.inventory_level}, Inventory: 0")
                self.stockouts += 1
                self.inventory_level = 0

            self.inventory_levels.append(self.inventory_level)
            self.total_holding_cost += self.inventory_level * self.holding_cost

    def inventory_monitor(self):
        while True:
            yield self.env.timeout(1)
            if self.inventory_level < self.s:
                order_qty = self.S - self.inventory_level
                self.total_ordering_cost += self.order_cost
                self.log(f"Placing order for {order_qty} units")
                self.env.process(self.receive_order(order_qty))

    def receive_order(self, amount):
        lead_time = self.lead_time_func()
        self.log(f"Order of {amount} units will arrive in {lead_time} days")
        yield self.env.timeout(lead_time)
        self.inventory_level += amount
        self.log(f"Order of {amount} units received. Inventory: {self.inventory_level}")

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


def run_simulation(s=20, S=100, sim_time=365, seed=42, verbose=True):
    random.seed(seed)

    # Lead time: Uniform(1, 5)
    lead_time_func = lambda: random.randint(1, 5)

    # Daily demand: Poisson(20)
    demand_func = lambda: random.normalvariate(20,1)

    order_cost = 50
    holding_cost = 1

    env = simpy.Environment()
    system = InventorySystem(env, s, S, lead_time_func, demand_func, order_cost, holding_cost, sim_time, verbose=verbose)
    env.run(until=sim_time)

    kpis = system.get_kpis()
    print("\n=== Simulation KPIs ===")
    for k, v in kpis.items():
        print(f"{k}: {v}")
    return kpis


if __name__ == "__main__":
    run_simulation()
