import heapq


class TransportGraph:
    def __init__(self):
        self.stations = []
        self.routes = {}

    def add_station(self, name):
        if name not in self.routes:
            self.stations.append(name)
            self.routes[name] = []

    def add_route(self, from_station, to_station, weight, bidirectional=True):
        self.add_station(from_station)
        self.add_station(to_station)
        self.routes[from_station].append((to_station, weight))
        if bidirectional:
            self.routes[to_station].append((from_station, weight))

    def shortest_path_Dijkstra(self, start):
        if start not in self.routes:
            raise ValueError("Нет такой станции")
        distances = {station: float("inf") for station in self.stations}
        distances[start] = 0
        queue = [(0, start)]

        while queue:
            current_distance, station = heapq.heappop(queue)
            if current_distance != distances[station]:
                continue
            for neighbor, weight in self.routes[station]:
                if weight < 0:
                    raise ValueError("Дейкстра не работает с отрицательными весами")
                new_distance = current_distance + weight
                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    heapq.heappush(queue, (new_distance, neighbor))
        return distances

    def shortest_path_BellmanFord(self, start):
        if start not in self.routes:
            raise ValueError("Нет такой станции")
        distances = {station: float("inf") for station in self.stations}
        distances[start] = 0
        edges = []
        for station in self.stations:
            for neighbor, weight in self.routes[station]:
                edges.append((station, neighbor, weight))

        for _ in range(len(self.stations) - 1):
            changed = False
            for from_station, to_station, weight in edges:
                if distances[from_station] != float("inf") and distances[from_station] + weight < distances[to_station]:
                    distances[to_station] = distances[from_station] + weight
                    changed = True
            if not changed:
                break

        for from_station, to_station, weight in edges:
            if distances[from_station] != float("inf") and distances[from_station] + weight < distances[to_station]:
                raise ValueError("Обнаружен отрицательный цикл")
        return distances

    def all_pairs_shortest_paths_FloydWarshall(self):
        size = len(self.stations)
        distances = [[float("inf")] * size for _ in range(size)]
        indexes = {station: index for index, station in enumerate(self.stations)}

        for index in range(size):
            distances[index][index] = 0
        for station in self.stations:
            for neighbor, weight in self.routes[station]:
                i = indexes[station]
                j = indexes[neighbor]
                distances[i][j] = min(distances[i][j], weight)

        for middle in range(size):
            for start in range(size):
                for finish in range(size):
                    new_distance = distances[start][middle] + distances[middle][finish]
                    if new_distance < distances[start][finish]:
                        distances[start][finish] = new_distance
        return distances


class NetworkOptimizer:
    def __init__(self, graph):
        self.graph = graph

    def _edges(self):
        edges = []
        used = set()
        for station in self.graph.stations:
            for neighbor, weight in self.graph.routes[station]:
                key = frozenset((station, neighbor))
                if station != neighbor and key not in used:
                    used.add(key)
                    edges.append((weight, station, neighbor))
        return edges

    def minimum_spanning_tree_Kruskal(self):
        parent = {station: station for station in self.graph.stations}

        def find(station):
            while parent[station] != station:
                parent[station] = parent[parent[station]]
                station = parent[station]
            return station

        tree = []
        total_weight = 0
        for weight, first, second in sorted(self._edges()):
            first_root = find(first)
            second_root = find(second)
            if first_root != second_root:
                parent[first_root] = second_root
                tree.append((first, second, weight))
                total_weight += weight
        if len(tree) != len(self.graph.stations) - 1:
            raise ValueError("Граф несвязный")
        return tree, total_weight

    def minimum_spanning_tree_Prim(self, start=None):
        if not self.graph.stations:
            return [], 0
        start = start or self.graph.stations[0]
        visited = {start}
        queue = [(weight, start, neighbor) for neighbor, weight in self.graph.routes[start]]
        heapq.heapify(queue)
        tree = []
        total_weight = 0

        while queue and len(visited) < len(self.graph.stations):
            weight, first, second = heapq.heappop(queue)
            if second in visited:
                continue
            visited.add(second)
            tree.append((first, second, weight))
            total_weight += weight
            for neighbor, next_weight in self.graph.routes[second]:
                if neighbor not in visited:
                    heapq.heappush(queue, (next_weight, second, neighbor))
        if len(visited) != len(self.graph.stations):
            raise ValueError("Граф несвязный")
        return tree, total_weight


def print_distances(title, distances):
    print(title)
    for station, distance in distances.items():
        print(f"{station}: {distance}")


def main():
    graph = TransportGraph()
    routes = [
        ("Центральный вокзал", "Площадь Ленина", 1.2),
        ("Центральный вокзал", "Автостанция-1", 3.5),
        ("Центральный вокзал", "Вокзал-Северный", 4.0),
        ("Площадь Ленина", "Автостанция-1", 2.1),
        ("Площадь Ленина", "Университет", 0.8),
        ("Площадь Ленина", "Автостанция-2", 3.0),
        ("Площадь Ленина", "Парковая", 1.5),
        ("Автостанция-1", "Автостанция-2", 5.4),
        ("Автостанция-1", "Портовая", 4.2),
        ("Университет", "Вокзал-Северный", 2.7),
        ("Университет", "Автостанция-2", 1.9),
        ("Вокзал-Северный", "Парковая", 3.3),
        ("Вокзал-Северный", "Портовая", 6.0),
        ("Автостанция-2", "Парковая", 2.5),
    ]

    for from_station, to_station, weight in routes:
        graph.add_route(from_station, to_station, weight)

    print_distances("Кратчайшие пути от Центрального вокзала (Дейкстра):", graph.shortest_path_Dijkstra("Центральный вокзал"))
    print()
    print_distances("Кратчайшие пути от Центрального вокзала (Беллман-Форд):", graph.shortest_path_BellmanFord("Центральный вокзал"))
    print()
    print("Матрица кратчайших расстояний (Флойд-Уоршелл):")
    for row in graph.all_pairs_shortest_paths_FloydWarshall():
        print(row)
    print()

    optimizer = NetworkOptimizer(graph)
    kruskal_tree, kruskal_weight = optimizer.minimum_spanning_tree_Kruskal()
    prim_tree, prim_weight = optimizer.minimum_spanning_tree_Prim()
    print("Минимальная сеть (Крускал):", kruskal_tree)
    print("Суммарный вес:", kruskal_weight)
    print("Минимальная сеть (Прим):", prim_tree)
    print("Суммарный вес:", prim_weight)


if __name__ == "__main__":
    main()
