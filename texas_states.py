import json


with open('states_area.json', 'r') as states:
    data = json.load(states)

total_area_of_states = 0
area_of_texas = 268596
states_that_fit_in_texas = []


for item in sorted(data, key=lambda x: int(x[1])):
    if item[1] < area_of_texas:
        if (item[1] + total_area_of_states) < area_of_texas:
            total_area_of_states = item[1] + total_area_of_states
            states_that_fit_in_texas.append(item[0])

print(states_that_fit_in_texas)
print(total_area_of_states)
print(len(states_that_fit_in_texas))