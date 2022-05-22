import random
import threading
from typing import List

import numpy as np
import pygad

from core.data_model import DataModel
from . import Solver


class MockSolver(Solver):
    def __init__(self, data: DataModel):
        super(MockSolver, self).__init__(data)

    def gen_initial_population(self, size=20):
        """
        Initial population format
        """
        ids = np.array([s.id for s in self.data.spots if s.id != 0])
        initial_population = []

        for _ in range(size):
            array_copy = ids.copy()
            random.shuffle(array_copy)
            initial_population.append(array_copy)

        return initial_population

    def mutation(self, offspring, ga_instance):
        # Swap mutation
        def swap(x, y):
            x, y = y, x

        for chromosome_idx in range(offspring.shape[0]):
            random_gene_x_idx = np.random.choice(range(offspring.shape[1]))
            random_gene_y_idx = np.random.choice(range(offspring.shape[1]))

            aux = offspring[chromosome_idx, random_gene_x_idx]
            offspring[chromosome_idx,
                      random_gene_x_idx] = offspring[chromosome_idx, random_gene_y_idx]
            offspring[chromosome_idx, random_gene_y_idx] = aux

        return offspring

    def aex_crossover(self, parent1: np.array, parent2: np.array):
        result = [parent1[0], parent1[1]]
        remaining = [i for i in parent1 if i not in result]

        # Take child from: parent2 if True else parent1
        flag = True
        while len(result) != len(parent1):
            alt_parent = parent2 if flag else parent1
            cur = result[-1]

            value_idx = np.where(alt_parent == cur)[0][0]
            if value_idx == len(alt_parent) - 1 or alt_parent[value_idx + 1] in result:
                # If there is no next element after cur or next element exists already: select random remaining
                selected = random.choice(remaining)
            else:
                # Select next element
                selected = alt_parent[value_idx + 1]

            result.append(selected)
            remaining.remove(selected)
            flag = not flag

        # print(f"Crossover between {parent1} and {parent2}: {result}")

        return np.array(result)

    def crossover(self, parents, offspring_size, ga_instance):
        n = parents.shape[1]
        offspring = []
        idx = 0
        while len(offspring) != offspring_size[0]:
            parent1 = parents[idx % parents.shape[0], :].copy()
            parent2 = parents[(idx + 1) % parents.shape[0], :].copy()

            result = self.aex_crossover(parent1, parent2)

            offspring.append(result)

            idx += 1

        return np.array(offspring)

    def fitness(self, solution_vector, solution_idx):
        solution_vector = [int(i) for i in solution_vector]
        routes = self.decode_routes(solution_vector)
        fitness_value = 0
        max_path_cost = 0
        sum_path_cost = 0

        inf = 9999999999999999

        # If solution is not feasible, return -oo
        if [] in routes:
            return -inf

        def distance(id1, id2):
            return abs(self.data.spots[id1].x - self.data.spots[id2].x) ** 2 + \
                abs(self.data.spots[id1].y - self.data.spots[id2].y) ** 2

        for route in routes:
            path_cost = distance(0, route[0]) + distance(route[-1], 0)

            for i in range(1, len(route)):
                path_cost += distance(route[i - 1], route[i])

            sum_path_cost += path_cost
            max_path_cost = max(max_path_cost, path_cost)

        return -(np.log(sum_path_cost) ** 3)

    def decode_routes(self, individual_route: List[int]):
        """
        Decode routes based on total path length
        Each vehicle will take spots until it can't. So
        if 1 vehicle can make the entire path, the rest will not be used
        """
        routes = []

        vehicle_capacity = self.data.capacity
        sub_route = []
        vehicle_load = 0
        elapsed_time = 0
        last_spot = 0

        for spot_idx in individual_route:
            due_time = self.data.spots[spot_idx].due_time
            ready_time = self.data.spots[spot_idx].ready_time

            demand = self.data.spots[spot_idx].demand
            updated_vehicle_load = vehicle_load + demand

            depot_time = self.data.spots[spot_idx].depot_time
            updated_elapsed_time = elapsed_time + \
                self.data.time_matrix[last_spot][spot_idx] + \
                depot_time

            # Validate vehicle load and elapsed time
            if updated_vehicle_load <= vehicle_capacity and ready_time <= updated_elapsed_time and updated_elapsed_time <= due_time:
                # Add to current subroute
                sub_route.append(spot_idx)
                vehicle_load = updated_vehicle_load
                elapsed_time = updated_elapsed_time
            else:
                # Vehicle can't move further, save current subroute
                routes.append(sub_route)

                # Initialize new subroute
                sub_route = [spot_idx]
                vehicle_load = demand
                elapsed_time = self.data.time_matrix[0][spot_idx] + depot_time
            last_spot = spot_idx

        if sub_route != []:
            # Save last sub_route if not empty
            routes.append(sub_route)

        return routes

    def _print_summary(self, routes, value):
        print(f"Best fitness: {value}")
        print("Routes:")

        for idx, route in enumerate(routes):
            route_str = " -> ".join([str(i) for i in [0] + route + [0]])
            print(f"Route {idx + 1}: {route_str}")

    def solve(self, num_generations=500, verbose=False):
        def mutation(x, y): return self.mutation(x, y)
        def crossover(x, y, z): return self.crossover(x, y, z)
        def fitness(x, y): return self.fitness(x, y)

        ga_instance = pygad.GA(num_generations=num_generations,
                               num_parents_mating=8,
                               fitness_func=fitness,
                               mutation_percent_genes=0.1,
                               mutation_type=mutation,
                               mutation_num_genes=1,
                               mutation_probability=0.1,
                               delay_after_gen=0,
                               crossover_type=crossover,
                               initial_population=self.gen_initial_population(),
                               allow_duplicate_genes=False
                               )
        ga_instance.run()
        solution, value, _ = ga_instance.best_solution()
        routes = self.decode_routes([int(i) for i in solution])

        if verbose:
            self._print_summary(routes, value)
            ga_instance.plot_fitness()

        if len(routes) > self.data.num_vehicles:
            raise Exception("No feasible solution found.")

        return routes
