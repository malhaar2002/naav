from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

class TSP:
    def __init__(self):
        pass

    def create_data_model(self, coordinates):
        """Stores the data for the problem."""
        data = {}
        data['distance_matrix'] = self.calculate_distance_matrix(coordinates)  # Yields the distance matrix
        data['num_vehicles'] = 1
        data['depot'] = 0
        return data
    
    def distance(self, point1, point2):
        return ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2) ** 0.5

    def calculate_distance_matrix(self, coordinates):
        n = len(coordinates)
        distances = [[0.0 for _ in range(n)] for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if i != j:
                    distances[i][j] = self.distance(coordinates[i], coordinates[j])
        return distances
    
    def get_solution(self, manager, routing, solution):
        """Returns the solution as a list of node indices."""
        index = routing.Start(0)
        route = [manager.IndexToNode(index)]
        while not routing.IsEnd(index):
            index = solution.Value(routing.NextVar(index))
            route.append(manager.IndexToNode(index))
        return route[:-1]  # Exclude the return to the depot

    def print_solution(self, manager, routing, solution):
        """Prints solution on console."""
        print('Objective: {} miles'.format(solution.ObjectiveValue()))
        index = routing.Start(0)
        plan_output = 'Route for vehicle 0:\n'
        route_distance = 0
        while not routing.IsEnd(index):
            plan_output += ' {} ->'.format(manager.IndexToNode(index))
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(previous_index, index, 0)
        plan_output += ' {}\n'.format(manager.IndexToNode(index))
        print(plan_output)
        return plan_output  # You can modify this part to fit your output needs

    def solve_tsp(self, coordinates):
        # Instantiate the data problem.
        data = self.create_data_model(coordinates)

        # Create the routing index manager.
        manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']), data['num_vehicles'], data['depot'])

        # Create Routing Model.
        routing = pywrapcp.RoutingModel(manager)

        # Create and register a transit callback.
        def distance_callback(from_index, to_index):
            # Returns the distance between the two nodes.
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return data['distance_matrix'][from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)

        # Define cost of each arc.
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # Setting first solution heuristic.
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

        # Solve the problem.
        solution = routing.SolveWithParameters(search_parameters)

        # Print solution on console.
        if solution:
            # return self.print_solution(manager, routing, solution)
            return self.get_solution(manager, routing, solution)

# Example usage
# coordinates = [
#     (10.391379, 8.405525),
#     (14.780237, 7.036543),
#     (1.511838, 6.366090),
#     (9.276912, 5.418818),
#     (11.376465, 4.216809)
# ]

# import numpy as np

# # Generate random coordinates for 50 cities
# np.random.seed(42)  # For reproducibility
# cities_coordinates = np.random.uniform(low=-90, high=90, size=(50, 2))  # Latitude and Longitude


# Calculate the tour using branch and bound
# tour = TSP().solve_tsp(cities_coordinates)

# # Output the tour
# for city in tour:
#     print(city, end=' ')
# print(tour[0])  # Return to the starting city