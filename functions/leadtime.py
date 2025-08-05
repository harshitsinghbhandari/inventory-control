import numpy as np
def positive_normal_lead_time_generator(mu: float = 2, sigma: float = 0.5):
    """
    Infinite generator yielding positive lead times from a normal distribution.
    
    Parameters:
    - mu: mean of the normal distribution
    - sigma: standard deviation of the normal distribution
    
    Yields:
    - A positive sample from the normal distribution each time next() is called
    """
    while True:
        lead_time = round(np.random.normal(loc=mu, scale=sigma))
        if lead_time > 0:
            yield lead_time

def log_normal_lead_time_generator(mu: float = 1.2, sigma: float = 0.6):
    """
    Infinite generator yielding lead times following a log-normal distribution.
    
    Parameters:
    - mu: mean of the underlying normal distribution (log scale)
    - sigma: standard deviation of the underlying normal distribution (log scale)
    
    Yields:
    - A single random sample of lead time each time next() is called
    """
    while True:
        lead_time = round(np.random.lognormal(mean=mu, sigma=sigma))
        yield lead_time
def amount_based_lead_time_generator(a: float=0.1, b: float=0.5, mu: float = 0.0, sigma: float = 0.1):
    """
    Yield lead time based on amount ordered, with randomness.
    
    Args:
        a: scaling factor for amount
        b: exponent for nonlinear growth
        mu: mean of log-normal noise (usually 0)
        sigma: standard deviation of log-normal noise
    """
    while True:
        amount = yield  # wait for amount input
        if amount is None:
            continue
        base_time = (a * (int(amount) ** b))
        noise = np.random.lognormal(mean=mu, sigma=sigma)
        lead_time = base_time * noise
        yield lead_time