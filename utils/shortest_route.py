import sys
import os

# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from algorithms.shortest_path_finder_algorithm import ShortestPathFinderAlgorithm
import threading
import json

class ShortestRoute:
    def __init__(self, json_file):
        self.json_file = json_file
        self.lock = threading.Lock()  # Lock for synchronization
        with open(json_file, 'r') as f:
            self.data = json.load(f)
        self.ShortestPathFinder = ShortestPathFinderAlgorithm(self.json_file)

    def __find_node_name(self, arduino_id):
        with self.lock:
            for node_id, node_info in self.data['node_detail'].items():
                if node_id == arduino_id:
                    return node_info['node_name']
            return None

    def get_shortest_route(self, arduino_id):
        node_name = self.__find_node_name(arduino_id)
        with self.lock:
            if node_name is None:
                print(f"Error: Node not found for Arduino ID '{
                    arduino_id}'.")
                return None
            try:
                shortest_route = self.ShortestPathFinder.get_shortest_path(
                    node_name)
                return shortest_route
            except Exception as e:
                print(e)

    def get_arduino_ids_from_node_name(self, node_name_list):
        arduino_ids = []
        with self.lock:
            for node_name in node_name_list:
                for key, value in self.data["node_detail"].items():
                    if value["node_name"] == node_name:
                        arduino_ids.append(key)
        return arduino_ids


if __name__ == "__main__":
    # Example usage
    json_file = r'data\node_connection_graph.json'
    shortest_route = ShortestRoute(json_file)

    print(shortest_route.get_shortest_route("1"))
    print(shortest_route.get_arduino_id_from_node_name(['B', 'C', 'D']))
