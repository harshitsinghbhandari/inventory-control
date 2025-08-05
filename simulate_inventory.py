# Import the modules
import simpy
import random
import statistics
import logging
import matplotlib.pyplot as plt
from dataclasses import dataclass
# Import the necessary helper functions
from utils.log_setup import setup_logger
from functions.leadtime import positive_normal_lead_time_generator, log_normal_lead_time_generator
from functions.demand import ar1_demand_generator, lumpy_ar1_demand_generator
logger = setup_logger('InventoryLogger', 'inventory.log')

LIVEORDER = False
# A dictionary to map demand and lead time functions to their respective generators
generator_list = {
    'log_normal_lt': log_normal_lead_time_generator,
    'positive_normal_lt': positive_normal_lead_time_generator,
    'ar1_demand': ar1_demand_generator,
    'lumpy_ar1_demand': lumpy_ar1_demand_generator
}

# Custom logging filter to add the current day to log records
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
        # Environment Variables
        self.env = env
        self.s = s
        self.S = S
        self.order_cost = order_cost
        self.holding_cost = holding_cost
        self.simulation_time = simulation_time
        self.verbose = verbose
        # Demand and Lead Time Generators Params
        self.muPositiveNormal = 2
        self.sigmaPositiveNormal = 0.5
        self.muLogNormal = 1.2
        self.sigmaLogNormal = 0.6
        self.muAR1 = 4
        self.sigmaAR1 = 4
        self.base_demand = 50
        self.min_demand = 0
        self.pOccurence = 0.8
        self.phi=0.8
        # Demand and Lead Time Generators
        self.demand_gen = ar1_demand_generator()
        self.lead_time_gen = positive_normal_lead_time_generator()

        # State
        self.inventory_level = S
        self.order_limit = 1*S

        # KPIs
        self.total_demand = 0
        self.total_fulfilled = 0
        self.stockouts = 0
        self.inventory_levels = []
        self.orders={}
        self.order_received = []
        self.lost_sales = []
        self.lead_times = []
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
        return next(self.lead_time_gen)

# ============ Customer Demand Process =============
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
# ============ Inventory Monitoring Process =============
    def inventory_monitor(self):
        global LIVEORDER
        while True:
            yield self.env.timeout(1)
            if self.inventory_level < self.s and not LIVEORDER:
                print(f"Current orders: {sum(list(self.orders.values())) - sum(self.order_received)}")
                order_qty = self.S - self.inventory_level
                self.total_ordering_cost += self.order_cost
                self.orders[self.env.now] = order_qty
                self.log(f"Placing order for {order_qty} units (Inventory: {self.inventory_level}, Threshold: {self.s})")
                LIVEORDER = True
                self.env.process(self.receive_order(order_qty))
# ============ Order Receiving Process =============
    def receive_order(self,amount):
        global LIVEORDER
        lead_time = self.lead_time_func()
        # lead_time = 1
        self.log(f"Order of {amount} units will arrive in {lead_time} days")
        self.lead_times.append(lead_time)
        yield self.env.timeout(lead_time)
        LIVEORDER = False
        self.inventory_level += amount
        self.log(f"Order of {amount} units received. Inventory: {self.inventory_level}")
        self.order_received.append(amount)

# ============ KPI Calculation =============
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
            ,'lead_times': self.lead_times
        }   

# ============= Simulation Function =============
def run_simulation(s=20, S=100, sim_time=365, seed=42, verbose=True,demand_func='lumpy_ar1_demand', lead_time_func=None,muLeadTime=4,sigmaLeadTime=2,MuLogNormal=1.2,sigmaLogNormal=0.6,muAR1=0,sigmaAR1=4,base_demand=20,min_demand=0,pOccurence=0.8,phi=0.8):
    random.seed(seed)

    order_cost = 50
    holding_cost = 1
    sim_time = sim_time

    env = simpy.Environment()
    system = InventorySystem(env, s, S, order_cost, holding_cost, sim_time, verbose=verbose)
    system.muPositiveNormal = muLeadTime
    system.sigmaPositiveNormal = sigmaLeadTime
    system.muLogNormal = MuLogNormal
    system.sigmaLogNormal = sigmaLogNormal
    system.muAR1 = muAR1
    system.sigmaAR1 = sigmaAR1
    system.base_demand = base_demand
    system.min_demand = min_demand
    system.pOccurence = pOccurence
    system.phi=phi
    
    match demand_func:
        case 'ar1_demand':
            system.demand_gen = generator_list[demand_func](mu=system.muAR1, sigma=system.sigmaAR1, base_demand=system.base_demand, min_demand=system.min_demand,phi=system.phi)
        case 'lumpy_ar1_demand':
            system.demand_gen = generator_list[demand_func](mu=system.muAR1, sigma=system.sigmaAR1, base_demand=system.base_demand, min_demand=system.min_demand, p_occurence=system.pOccurence,phi=system.phi)
    match lead_time_func:
        case 'log_normal_lt':
            system.lead_time_gen = generator_list[lead_time_func](system.muLogNormal, system.sigmaLogNormal)
        case 'positive_normal_lt':
            system.lead_time_gen = generator_list[lead_time_func](system.muPositiveNormal, system.sigmaPositiveNormal)
    env.run(until=sim_time)
    kpis = system.get_kpis()

    print("\n=== Simulation KPIs ===")
    print(kpis)
    print(f"Running simulation with parameters: s={s}, S={S}, simulation_time={sim_time}, seed={seed}, demand_func={demand_func}, lead_time_func={lead_time_func}, muLeadTime={muLeadTime}, sigmaLeadTime={sigmaLeadTime}, MuLogNormal={MuLogNormal}, sigmaLogNormal={sigmaLogNormal}, muAR1={muAR1}, sigmaAR1={sigmaAR1}, base_demand={base_demand}, min_demand={min_demand}, pOccurence={pOccurence}, phi={phi}")
    return kpis, system.get_data()
# ============= Plotting Function =============
def plot_inventory_levels(inventory_data,save=False):
    plt.figure(figsize=(12, 6))
    plt.plot(inventory_data['inventory_levels'], label='Inventory Level', color='blue', marker='o', markersize=2)
    plt.title('Inventory Levels Over Time')
    plt.xlabel('Days')
    plt.ylabel('Inventory Level')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    if save:
        plt.savefig('static/inventory_levels.png')
    else:
        plt.show()


if __name__ == "__main__":
    kpis,data=run_simulation(s=20,S=100)
    print("\n=== Simulation KPIs ===")
    for k, v in kpis.items():
        print(f"{k}: {v}")
    plot_inventory_levels(data)
    for k, v in data.items():
        print(f"{k}: {list(v)[:10]}...")
        print(f"Average {k}: {statistics.mean(list(v)):.2f}")
    print(f"Total Lost Sales: {sum(data['lost_sales'])}")