import pandas as pd
import numpy as np
from numpy import random
import matplotlib.pyplot as plt
import requests
from datetime import timedelta

plt.ion()

STATS_FILE = 'covid_stats_usa.xlsx'
TOTAL_DAYS = 150
DRIFT = 0.0016
NO_OF_SIMS = 400
POPULATION_SIZE = 329000000

# Load Data from Stats File
# covid = pd.read_excel(STATS_FILE)
# covid.set_index(['date'], drop=True, inplace=True)

# Load Data via API
base_url = 'https://covidtracking.com'
resource_url = '/api/v1/us/daily.json'
r = requests.get(url=base_url + resource_url)
covid = pd.DataFrame(r.json())
covid.date = pd.to_datetime(covid.date, format='%Y%m%d')
covid.set_index('date', inplace=True)
covid.sort_index(inplace=True)
covid = covid.rename(columns={'positive': 'total_cases', 'positiveIncrease': 'new_cases'})
# covid['new_cases'] = covid.total_cases.diff()
covid['growth_factor'] = covid.new_cases.pct_change() + 1


def gf_monte_carlo(days_to_sim, mu, sigma, drift):
    x = np.array(range(days_to_sim))
    b = random.normal(mu, sigma, size=days_to_sim)
    y = -drift * x + b
    for i, g in enumerate(y):
        dn_cases = covid.new_cases[-1] * pd.Series(y[:i + 1]).cumprod()
        n_cases = (covid.total_cases[-1] + dn_cases.cumsum()).iloc[-1]
        y[i] = g * (1 - (n_cases / POPULATION_SIZE))
    return y


def gf_mc_old(days_to_sim, mu, sigma, drift):
    gf_li = []
    for d in range(days_to_sim):
        new_mu = mu - (d // 1) * drift
        gf = random.normal(new_mu, sigma)
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


days_to_sim = TOTAL_DAYS - len(covid.index)
mu = covid.growth_factor[-13:].mean()
sigma = covid.growth_factor[-13:].std() - 0.05
# pop_factor = POPULATION_SIZE / covid.total_cases[-1]

sims_df = pd.DataFrame(index=pd.date_range(covid.index[-1] + timedelta(1), periods=days_to_sim))

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
plt.plot(covid.total_cases)
for sim in total_cases:
    plt.plot(total_cases[sim])

# Plot daily new cases of each simulation over time
# plt.plot(covid.new_cases)
# for sim in daily_new_cases:
#     plt.plot(daily_new_cases[sim])

# Plot growth factor of each simulation over time
# plt.plot(covid.growth_factor)
# for sim in sims_df:
#     plt.plot(sims_df[sim])
