import json
import threading


class GetNodeStatus:
    def __init__(self, json_file):
        self.json_file = json_file
        self.lock = threading.Lock()  # Lock for synchronization
        with open(json_file, 'r') as f:
            self.data = json.load(f)

    def get_status(self, arduino_id):
        node_name = self.__find_node_name(arduino_id)
        if node_name:
            with self.lock:
                with open(self.json_file, 'r') as f:
                    data = json.load(f)
                    return data["node_current_status"][node_name]["status"]
            
    def get_current_cap_status(self, arduino_id):
        node_name = self.__find_node_name(arduino_id)
        if node_name:
            with self.lock:
                with open(self.json_file, 'r') as f:
                    data = json.load(f)
                    return data["node_current_status"][node_name]["current_cap_status"]

    def __find_node_name(self, arduino_id):
        for node_id, node_info in self.data['node_detail'].items():
            if node_id == arduino_id:
                return node_info['node_name']
        return None


if __name__ == "__main__":
    # Example usage
    json_file = r'data\node_connection_graph.json'
    getter = GetNodeStatus(json_file)

    # Get node status
    print(getter.get_status("1"))

    # Get current_cap_status
    print(getter.get_current_cap_status("1"))
