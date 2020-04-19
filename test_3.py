import json


with open('covid_dashboard/location_list.json', 'r') as f:
    locations = f.read()

locations = json.loads(locations)

with open('covid_dashboard/population.json', 'r') as f:
    populations = f.read()

populations = json.loads(populations)

for location in locations.keys():
    for location_population in populations:
        loc = location_population['country'].strip().upper().replace(' ', '_').replace(',', '_')
        if loc in location:
            locations[location]['population'] = location_population['population']
            break
    if locations[location].get('population') is None:
        locations[location]['population'] = None


with open('covid_dashboard/new_locations_with_populations.json', 'w') as f:
    f.write(json.dumps(locations))

