import json
from typing import List


class Spot:
    def __init__(self, id, x, y, demand, ready_time, due_time, depot_time):
        self.id = id
        self.x = x
        self.y = y
        self.demand = demand
        self.ready_time = ready_time
        self.due_time = due_time
        self.depot_time = depot_time


class Vehicle:
    def __init__(self, id, capacity):
        self.id = id
        self.capacity = capacity


class ParsedData:
    spots: List[Spot]
    time_matrix: List[List[float]]
    num_vehicles: int
    capacity: int

    def __init__(self, spots, time_matrix, num_vehicles, capacity):
        self.spots = spots
        self.time_matrix = time_matrix
        self.num_vehicles = num_vehicles
        self.capacity = capacity


def parse_json(json_data):
    spots = [Spot(s['id'], s['x'], s['y'], s['demand'], s['ready_time'],
                  s['due_time'], s['depot_time']) for s in json_data['spots']]

    time_matrix = json_data['time_matrix']
    num_vehicles = json_data['num_vehicles']
    capacity = json_data['capacity']

    return ParsedData(spots, time_matrix, num_vehicles, capacity)


class DataModel:
    def __init__(self, data: ParsedData = None):
        if data is not None:
            self.spots: List[Spot] = data.spots
            self.time_matrix = data.time_matrix
            self.num_vehicles = data.num_vehicles
            self.capacity = data.capacity

    @staticmethod
    def from_json(path):
        fd = open(path, 'r')
        json_data = json.load(fd)
        parsed = parse_json(json_data)
        return DataModel(parsed)
