import json


class ShortestPathFinderAlgorithm:
    def __init__(self, file_path):
        self.file_path = file_path
        

    def load_graph_data(self, file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data

    def dijkstra(self, source, destination, graph_data):
        graph_link = graph_data['graph_link']
        node_status = graph_data['node_current_status']

        distances = {node: float('inf') for node in graph_link}
        distances[source] = 0
        visited = {}
        unvisited = set(graph_link.keys())

        while unvisited:
            current_node = min(unvisited, key=lambda node: distances[node])

            if current_node == destination:
                path = []
                while current_node != source:
                    path.append(current_node)
                    current_node = visited.get(current_node)
                    if current_node is None:
                        return None
                path.append(source)
                path.reverse()
                return path

            unvisited.remove(current_node)

            for neighbor, weight in graph_link[current_node].items():
                if node_status[neighbor]['status']:
                    distance = distances[current_node] + weight
                    if distance < distances[neighbor]:
                        distances[neighbor] = distance
                        visited[neighbor] = current_node

        return None

    def get_source_node(self, graph_data):
        for node, details in graph_data['node_detail'].items():
            if details['work'] == 'r':
                return details['node_name']
        return None

    def get_shortest_path(self, destination):
        graph_data = self.load_graph_data(self.file_path)
        source = self.get_source_node(graph_data)
        if source:
            path = self.dijkstra(source, destination, graph_data)
            if path:
                # print("Sequential order of visited nodes from",
                #       source, "to", destination, ":", path)
                return path
        #     else:
        #         print("There is no path from", source, "to", destination)
        # else:
        #     print("Source node with 'work': 'r' is not available.")
        return None


if __name__ == "__main__":
    file_path = "data/node_connection_graph.json"
    destination = 'D'
    path_finder = ShortestPathFinderAlgorithm(file_path)
    path_finder.get_shortest_path(destination)
