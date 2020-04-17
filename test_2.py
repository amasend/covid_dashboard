import requests
from postman_covid19_sdk.client import APIClient
import json

client = APIClient()
summary = client.get_summary()['Countries']

url = "https://api.covid19api.com/live/country/{country}/status/confirmed/date/2020-04-10T00:00:00Z"

payload = {}
headers = {}

data = []
locations = {}

for country in summary.index.values:
    slug = summary.loc[country]['Slug']
    response = requests.request("GET", url.format(country=slug), headers=headers, data=payload)
    data_ = response.json()
    if data_:
        data.append(data_[0])
        locations[country.strip().upper().replace(' ', '_').replace(',', '_')] = {'lat': data_[0]['Lat'], 'lon': data_[0]['Lon']}

with open('locations.json', 'w') as f:
    f.write(json.dumps(locations))
