import math
import random
from pprint import pprint
import json


def distance(x1, y1, x2, y2):
    return math.sqrt(abs(x1 - x2) ** 2 + abs(y1 - y2) ** 2)


def random_radius(r):
    return (2 * r) * (random.random() - .5)


if __name__ == "__main__":
    num_vehicles = 4
    num_spots = 10
    coord_radius = 500
    spots = [
        {
            "id": i,
            "x": 0 if i == 0 else random_radius(coord_radius),
            "y": 0 if i == 0 else random_radius(coord_radius),
            "demand": 0 if i == 0 else random.randrange(1, 40),
            "ready_time": 0 if i == 0 else random.randrange(0, 80),
            "depot_time": 1000000 if i == 0 else random.randrange(0, 40),
        }
        for i in range(num_spots)
    ]

    sum_demand = sum([i['demand'] for i in spots])
    capacity = max(math.ceil(sum_demand / num_vehicles),
                   num_spots * random.randrange(1, 20))

    for spot in spots:
        if spot['id'] != 0:
            spot["due_time"] = spot["ready_time"] + \
                spot["depot_time"] + random.randrange(50, coord_radius * 50)

        else:
            spot["due_time"] = 1000000

    time_matrix = []
    for i, spot1 in enumerate(spots):
        time_matrix.append([])
        for j, spot2 in enumerate(spots):
            # Time will be proportional to distance
            if i == j:
                time_matrix[-1].append(0)
            else:
                d = distance(spot1['x'], spot1['y'], spot2['x'], spot2['y'])
                time_matrix[-1].append(int(d / 10))

    data = {
        "spots": spots,
        "num_vehicles": num_vehicles,
        "capacity": capacity,
        "time_matrix": time_matrix
    }

    with open('./data.json', 'w') as fd:
        json.dump(data, fd, indent=2)
