from covid_dashboard.managers.data_manager import DataManager
import pandas as pd

manager = DataManager()

data = []

for i, location in enumerate(manager.locations.keys()):
    manager.download_data_for_location_one(location=location)

    manager.data_confirmed['Daily_growth_confirmed_pct'] = manager.compute_daily_growth_percentage(
        data=manager.data_confirmed['Cases'])
    manager.data_confirmed['Confirmed'] = manager.data_confirmed['Cases']
    manager.data_confirmed['Country'] = [location] * len(manager.data_confirmed)
    manager.data_confirmed.drop(['Cases'], axis=1, inplace=True)

    manager.data_confirmed['Daily_growth_recovered_pct'] = manager.compute_daily_growth_percentage(
        data=manager.data_recovered['Cases'])
    manager.data_confirmed['Recovered'] = manager.data_recovered['Cases']

    manager.data_confirmed['Daily_growth_deaths_pct'] = manager.compute_daily_growth_percentage(
        data=manager.data_deaths['Cases'])
    manager.data_confirmed['Deaths'] = manager.data_deaths['Cases']

    data.append(manager.data_confirmed)

data = pd.concat(data)
data.to_csv("covid.csv")
