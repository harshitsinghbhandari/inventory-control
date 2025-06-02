from simulate_inventory import run_simulation

def simulate_many():
    kpi_results = []
    data_results = []
    for i in range(20):
        for j in range(20):
            s = i * 5 + 5
            S = j * 5 + 10
            if s+20 <= S:
                continue
            # Run simulation with the current (s, S)
            kpis,data = run_simulation(s=s, S=S,verbose=False)

            kpi_results.append((s,S,kpis))
            data_results.append((s,S,data))

    return kpi_results, data_results
def leastStockouts(kpi_results, data_results):
    best_s, best_S = None, None
    min_stockouts = float('inf')

    for s, S, kpis in kpi_results:
        if kpis['Stockouts'] < min_stockouts:
            min_stockouts = kpis['Stockouts']
            best_s, best_S = s, S

    return best_s, best_S, min_stockouts
def bestFillRate(kpi_results, data_results):
    best_s, best_S = None, None
    max_fill_rate = float('-inf')
    fill_rate_95 = []
    for s, S, kpis in kpi_results:
        if kpis['Fill Rate'] > max_fill_rate:
            max_fill_rate = kpis['Fill Rate']
            best_s, best_S = s, S
    #     if kpis['Fill Rate'] >= 0.95:
    #         fill_rate_95.append((s, S, kpis['Fill Rate']))
    # if fill_rate_95:
    #     print(f"Fill rates >= 95%: {fill_rate_95}")
    return best_s, best_S, max_fill_rate
def bestAverageInventory(kpi_results, data_results):
    best_s, best_S = None, None
    max_avg_inventory = float('-inf')

    for s, S, kpis in kpi_results:
        if kpis['Average Inventory Level'] > max_avg_inventory:
            max_avg_inventory = kpis['Average Inventory Level']
            best_s, best_S = s, S

    return best_s, best_S, max_avg_inventory
def bestTotalCost(kpi_results, data_results):
    best_s, best_S = None, None
    min_total_cost = float('inf')
    for s, S, kpis in kpi_results:
        total_cost = kpis['Total Cost']
        if total_cost < min_total_cost:
            min_total_cost = total_cost
            best_s, best_S = s, S

    return best_s, best_S, min_total_cost
def bestTotalOrderingCost(kpi_results, data_results):
    best_s, best_S = None, None
    min_ordering_cost = float('inf')

    for s, S, kpis in kpi_results:
        ordering_cost = kpis['Total Ordering Cost']
        if ordering_cost < min_ordering_cost:
            min_ordering_cost = ordering_cost
            best_s, best_S = s, S

    return best_s, best_S, min_ordering_cost
def bestTotalHoldingCost(kpi_results, data_results):
    best_s, best_S = None, None
    min_holding_cost = float('inf')

    for s, S, kpis in kpi_results:
        holding_cost = kpis['Total Holding Cost']
        if holding_cost < min_holding_cost:
            min_holding_cost = holding_cost
            best_s, best_S = s, S

    return best_s, best_S, min_holding_cost
def leastLostOrders(kpi_results, data_results):
    best_s, best_S = None, None
    lostOrders = float('inf')

    def total(lst):
        return sum(int(i) for i in lst)

    for s, S, data in data_results:
        current_lost = total(data['lost_sales'])
        if current_lost < lostOrders:
            lostOrders = current_lost
            best_s, best_S = s, S

    return best_s, best_S, lostOrders

def bestFinder():
    kpi_results, data_results = simulate_many()
    best_s, best_S, min_stockouts = leastStockouts(kpi_results, data_results)
    print(f"Best (s, S) for least stockouts: ({best_s}, {best_S}) with {min_stockouts} stockouts")

    best_s, best_S, max_fill_rate = bestFillRate(kpi_results, data_results)
    print(f"Best (s, S) for best fill rate: ({best_s}, {best_S}) with fill rate {max_fill_rate}")

    best_s, best_S, max_avg_inventory = bestAverageInventory(kpi_results, data_results)
    print(f"Best (s, S) for highest average inventory: ({best_s}, {best_S}) with avg inventory {max_avg_inventory}")

    best_s, best_S, min_total_cost = bestTotalCost(kpi_results, data_results)
    print(f"Best (s, S) for lowest total cost: ({best_s}, {best_S}) with total cost {min_total_cost}")

    best_s, best_S, min_ordering_cost = bestTotalOrderingCost(kpi_results, data_results)
    print(f"Best (s, S) for lowest ordering cost: ({best_s}, {best_S}) with ordering cost {min_ordering_cost}")

    best_s, best_S, min_holding_cost = bestTotalHoldingCost(kpi_results, data_results)
    print(f"Best (s, S) for lowest holding cost: ({best_s}, {best_S}) with holding cost {min_holding_cost}")
    best_s, best_S, lostOrders = leastLostOrders(kpi_results, data_results)
    print(f"Best (s, S) for least lost orders: ({best_s}, {best_S}) with lost orders {lostOrders}")
if __name__ == "__main__":
    bestFinder()
    # Uncomment below to run the simulation with specific (s, S) values
    # s, S = 10, 30
    # kpis, data = run_simulation(s=s, S=S)
    # print(kpis)
    # print(data)
