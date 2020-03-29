# COVID-19 Simulation

This code takes existing COVID-19 case data and attempts to extrapolate total cases over time using Monte Carlo Simulations. This is a purely mathematical exercise intended to demonstrate the wide range of possible outcomes given initial conditions and assumptions. The model assumes the COVID-19 disease growth follows the logistic growth function.  The Logistic Function models growth in various applications such as population growth, tumor growth, neuron activation in Deep Neural Networks, and pandemics.  It is assumed that the Total Cases (N) of COVID-19 will follow the Logistic Function; the Daily New Cases (dN/dt) will follow the Logistic Distribution, the derivative of the Logistic Function; the Growth Factor then is the number of New Cases on any given day divided by the number of New Cases on the previous day.  Thus, when the growth factor is greater than  1.0, the number of Total Cases increases exponentially.  When the growth factor is 1.0, this is the "inflection point" of the Logistic Function where the number of Daily New Cases stabilizes (ceases to grow daily).

For COVID-19, it is expected that the Growth Factor will drop to 1.0 and eventually to 0 as the disease spreads through a population and the probability of infection drops as the population builds herd immunity.  There are several measures that can be taken to reduce the growth factor including social distancing, quarantining of infected individuals, reducing travel rate, hygiene, etc. This model does not attempt to explicitly take those factors into account and instead assumes their combined effect will result in a "drift" of the growth factor down from greater than 1.0 to eventually 0.

What this model attempts to simulate via Monte Carlo method is the possibility space of different Growth Factors on a daily basis.  The Growth Factor on any given day will be sampled from a random normal Gaussian distribution based on the mean (mu) and standard deviation (sigma) of Growth Factors from existing real world data (covid_stats_usa.xlsx file).  A "drift" rate is applied to reduce the mean daily during random sampling to account for various growth factor reduction measures such as social distancing.  Additionally, a probability of infection factor (1 - N/Population_Size) is used to cap the growth factor to ensure it doesn't result in total cases greater than the population.  As the total number of cases grows, the probabilty of infection reduces as already infected individuals are removed from the susceptible space.

There are several opportunities for optimization of this code outlined below.  Additionally, there are undoubtedly better and more rigorous models that stand up to scientific scrutiny.  One such model is the SIR model (https://scipython.com/book/chapter-8-scipy/additional-examples/the-sir-epidemic-model/) used by mathematicians and epidemiologists to model the spread of disease in a population.


There are several opportunities for improvement to this model in terms of code performance, model behavior, and assumptions.  Here is a list of a few in no order:
  - In function 'gf_monte_carlo,' random sampling happens one at a time to account for drift in mu (new_mu).  Sampling could be done at an array level.
  - The application of drift is arbritrary (reduce GF mean by a certain amount daily).  Drift could be defined in a more statistically precise manner.
  - Growth Factor distribution is assumed to be normal.  This may be a poor assumption as Growth Factor is heavily susceptible to external factors.
  - Due to drift being applied consistently over time, the model is unlikely to show "waves" of infection spread
  - To ensure the number of Total Cases does not exceed population size, a probability factor (1 - N/Population_Size) is applied to each random
    sample of Growth Factor.  This is mathematically lazy.
  - Another example of lazy mathematics is the way the code accounts for a randomly sampled Growth Factor of less than zero.  The code simply
    adjusts this to zero as it's impossible to have negative Growth Factor. This introduces a bias in sampling that accelerates how quickly
    the number of total cases reaches its limit in each simulation.
  - A major source of code performance inefficiency is the fact that n_cases has to be calculated after each random sample to account for the
    probability of infection (1 - n_cases/population_size).  There is undoubtedly a more efficient way to perform this calculation.
  - Ultimately, the goal is to randomly sample growth factors over time to model different scenarios.  There are probably multiple better methods
    of sampling and incorporating drift to simulate the way Growth Factor evolves over time.