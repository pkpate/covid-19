import pandas as pd
import numpy as np
from numpy import random
import matplotlib.pyplot as plt
from datetime import datetime as dt
from datetime import timedelta

plt.ion()

STATS_FILE = 'covid_stats_usa.xlsx'
TOTAL_DAYS = 150
DRIFT = 0.013
NO_OF_SIMS = 50
POPULATION_SIZE = 329000000


def gf_monte_carlo(days_to_sim, mu, sigma, drift):
    gf_li = []
    for d in range(days_to_sim):
        new_mu = mu - (d // 1) * drift
        gf = random.normal(new_mu - 0.1, sigma)
        if gf < 0:
            gf = 0
        if len(gf_li) > 0:
            dn_cases = covid.new_cases[-1] * pd.Series(gf_li).cumprod()
            n_cases = (covid.total_cases[-1] + dn_cases.cumsum()).iloc[-1]
        else:
            n_cases = 0
        gf = gf * (1 - (n_cases / POPULATION_SIZE))
        gf_li.append(gf)
    return gf_li


covid = pd.read_excel(STATS_FILE)
covid.set_index(['date'], drop=True, inplace=True)

days_to_sim = TOTAL_DAYS - len(covid.index)
mu = covid.growth_factor.mean()
sigma = covid.growth_factor.std()
# pop_factor = POPULATION_SIZE / covid.total_cases[-1]

sims_df = pd.DataFrame(index=pd.date_range(covid.index[-1], periods=days_to_sim))

for sim in range(NO_OF_SIMS):
    if sim % 100 == 0:
        print(f'Running simulation {sim + 1}...')
    sims_df[sim] = pd.Series(gf_monte_carlo(days_to_sim=days_to_sim,
                                            mu=mu,
                                            sigma=sigma,
                                            drift=DRIFT),
                             index=sims_df.index)

daily_new_cases = covid.new_cases[-1] * sims_df.cumprod()
total_cases = covid.total_cases[-1] + daily_new_cases.cumsum()

peak_daily_new_cases = daily_new_cases.max().max()

best_scenario_total_cases = int(total_cases.max().min())
worst_scenario_total_cases = int(total_cases.max().max())

print(f'Best Case Scenario Total Cases = {best_scenario_total_cases} people, {round(100 * best_scenario_total_cases / POPULATION_SIZE, 2)}% of population')
print(f'Worst Case Scenario Total Cases = {worst_scenario_total_cases} people, {round(100* worst_scenario_total_cases / POPULATION_SIZE, 2)}% of popluation')

# Plot total cases of each simulation over time
for sim in total_cases:
    plt.plot(total_cases[sim])
