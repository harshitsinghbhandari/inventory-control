from simulate_inventory import run_simulation
import matplotlib.pyplot as plt

def randomizing_alot(threshold, final, sim_time, seed, num_simulations=1000):
    results = []
    for i in range(num_simulations):
        print(f"Running simulation {i + 1}/{num_simulations}...")
        kpis = run_simulation(s=threshold, S=final, sim_time=sim_time, seed=seed + i,verbose=False)
        results.append(kpis)
    # Aggregate results
    aggregated_results = {
        "Fill Rate": sum(r["Fill Rate"] for r in results) / num_simulations,
        "Average Inventory Level": sum(r["Average Inventory Level"] for r in results) / num_simulations,
        "Stockouts": sum(r["Stockouts"] for r in results),
        "Total Ordering Cost": sum(r["Total Ordering Cost"] for r in results),
        "Total Holding Cost": sum(r["Total Holding Cost"] for r in results),
        "Total Cost": sum(r["Total Cost"] for r in results)
    }

    return aggregated_results
def change_parameters(s=20, S=100, sim_time=365, seed=42):
    results = []
    for i in range(15):
        for j in range(20):
            print(f"Running simulation with s={5+i}, S={5+i+j}...")
            kpis = run_simulation(s=5+i, S= 5+i+j*5, sim_time=sim_time, seed=seed, verbose=False)
            results.append(kpis)
    aggregated_results = {
        "Fill Rate": max(r["Fill Rate"] for r in results),
        "Average Inventory Level": max(r["Average Inventory Level"] for r in results),
        "Stockouts": min(r["Stockouts"] for r in results),
        "Total Ordering Cost": min(r["Total Ordering Cost"] for r in results),
        "Total Holding Cost": min(r["Total Holding Cost"] for r in results),
        "Total Cost": min(r["Total Cost"] for r in results)
    }
    all_results = {
        "Fill_Rate": [r["Fill Rate"] for r in results],
        "Average_Inventory_Level": [r["Average Inventory Level"] for r in results],
        "Stockouts": [r["Stockouts"] for r in results],
        "Total_Ordering_Cost": [r["Total Ordering Cost"] for r in results],
        "Total_Holding_Cost": [r["Total Holding Cost"] for r in results],
        "Total_Cost": [r["Total Cost"] for r in results]
    }
    return aggregated_results, all_results
if __name__ == "__main__":
    threshold = 20
    final = 100
    sim_time = 365
    seed = 42

    results,plotting_results = change_parameters(threshold, final, sim_time, seed)
    print("\n=== Monte Carlo Simulation Results ===")
    for k, v in results.items():
        print(f"{k}: {v}")
    print("\nSimulation completed.")
    plt.figure(figsize=(12, 6))
    plt.plot(plotting_results['Fill_Rate'], plotting_results["Average_Inventory_Level"], label='Inventory Level')
    plt.plot(plotting_results['Fill_Rate'], plotting_results["Stockouts"], label='Stockouts')
    # plt.plot(plotting_results['Fill_Rate'], plotting_results["Total_Cost"], label='Total Cost')
    plt.xlabel('Fill Rate')
    plt.ylabel('Values')
    plt.title('Monte Carlo Simulation Results')
    plt.legend()
    plt.grid()
    plt.show()