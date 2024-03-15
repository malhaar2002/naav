class TSP:
    # Function to calculate the distance between two points (Euclidean or non-Euclidean)
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

    # Function to compute the cost of a tour
    def tour_cost(self, tour, distances):
        cost = 0
        for i in range(len(tour) - 1):
            cost += distances[tour[i]][tour[i + 1]]
        cost += distances[tour[-1]][tour[0]]  # Return to the starting city
        return cost

    # Branch and Bound TSP Solver
    def tsp_branch_and_bound(self, coordinates):
        distances = self.calculate_distance_matrix(coordinates)
        n = len(distances)
        min_cost = float('inf')
        best_tour = None

        def bound(path):
            # Calculate lower bound using the minimum outgoing and incoming edges for each city
            bound = 0
            for i in range(n):
                if i not in path:
                    min_outgoing = min(distances[i][j] for j in range(n) if j != i)
                    min_incoming = min(distances[j][i] for j in range(n) if j not in path)
                    bound += min_outgoing + min_incoming
            return bound / 2  # Divide by 2 since we've counted each edge twice

        def backtrack(path, bound):
            nonlocal min_cost, best_tour

            if len(path) == n:
                # If we have visited all cities, check if it's a better tour
                cost = self.tour_cost(path, distances)
                if cost < min_cost:
                    min_cost = cost
                    best_tour = path[:]
            else:
                for city in range(n):
                    if city not in path:
                        new_bound = bound + distances[path[-1]][city]
                        if new_bound < min_cost:
                            backtrack(path + [city], new_bound)

        initial_bound = bound([])
        backtrack([0], initial_bound)

        return best_tour

coordinates = [
    (10.391379, 8.405525),
    (14.780237, 7.036543),
    (1.511838, 6.366090),
    (9.276912, 5.418818),
    (11.376465, 4.216809)
]

# Calculate the tour using branch and bound
tour = TSP().tsp_branch_and_bound(coordinates)

# Output the tour
for city in tour:
    print(city, end=' ')
print(tour[0])  # Return to the starting city