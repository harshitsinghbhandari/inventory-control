import simpy
import random
import statistics

class InventorySystem:
    def __init__(self, env, s, S, lead_time_func, demand_func, order_cost, holding_cost, simulation_time):
        self.env = env
        self.s = s
        self.S = S
        self.lead_time_func = lead_time_func
        self.demand_func = demand_func
        self.order_cost = order_cost
        self.holding_cost = holding_cost
        self.simulation_time = simulation_time

        # State variables
        self.inventory_level = S
        self.orders = []
        
        # KPIs
        self.total_demand = 0
        self.total_fulfilled = 0
        self.stockouts = 0
        self.inventory_levels = []
        self.total_ordering_cost = 0
        self.total_holding_cost = 0

        # Start simulation processes
        self.env.process(self.customer_demand())
        self.env.process(self.inventory_monitor())

    def customer_demand(self):
        while True:
            yield self.env.timeout(1)
            demand = self.demand_func()
            self.total_demand += demand

            if self.inventory_level >= demand:
                self.inventory_level -= demand
                self.total_fulfilled += demand
            else:
                self.stockouts += 1
                self.total_fulfilled += self.inventory_level
                self.inventory_level = 0
            
            self.inventory_levels.append(self.inventory_level)
            self.total_holding_cost += self.inventory_level * self.holding_cost

    def inventory_monitor(self):
        while True:
            yield self.env.timeout(1)
            if self.inventory_level < self.s:
                order_qty = self.S - self.inventory_level
                self.env.process(self.receive_order(order_qty))
                self.total_ordering_cost += self.order_cost

    def receive_order(self, amount):
        lead_time = self.lead_time_func()
        yield self.env.timeout(lead_time)
        self.inventory_level += amount

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


def run_simulation(s=20, S=100, sim_time=365, seed=42):
    random.seed(seed)

    # Lead time: Uniformly 1 to 5 days
    lead_time_func = lambda: random.randint(1, 5)

    # Daily demand: Poisson with mean 20
    demand_func = lambda: random.normalvariate(20,1)

    order_cost = 50
    holding_cost = 1  # per unit per day

    env = simpy.Environment()
    system = InventorySystem(env, s, S, lead_time_func, demand_func, order_cost, holding_cost, sim_time)
    env.run(until=sim_time)

    kpis = system.get_kpis()
    for k, v in kpis.items():
        print(f"{k}: {v}")
    return kpis


if __name__ == "__main__":
    run_simulation()
