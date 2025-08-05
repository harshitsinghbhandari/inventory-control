import random
def ar1_demand_generator(phi=0.5, mu=4, sigma=4, base_demand=50, min_demand=0):
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
def lumpy_ar1_demand_generator(
    phi=0.5,
    mu=0,
    sigma=8,
    base_demand=20,
    min_demand=0,
    p_occurence=0.8  # Probability that demand occurs in a time period
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
        if random.random() < p_occurence:
            # Step 2: Generate demand using AR(1)
            noise = random.normalvariate(mu, sigma)
            new_demand = phi * prev_demand + (1 - phi) * base_demand + noise
            new_demand = max(min_demand, int(round(new_demand)))
            prev_demand = new_demand
        else:
            new_demand = 0  # No demand this period

        yield new_demand