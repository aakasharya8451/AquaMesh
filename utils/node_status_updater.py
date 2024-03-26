import json
import threading


class NodeStatusUpdater:
    def __init__(self, json_file):
        self.json_file = json_file
        self.lock = threading.Lock()  # Lock for synchronization
        with open(json_file, 'r') as f:
            self.data = json.load(f)

    def update_node_status(self, arduino_id, new_status):
        node_name = self.__find_node_name(arduino_id)
        if node_name:
            with self.lock:
                with open(self.json_file, 'r+') as f:
                    data = json.load(f)
                    if data['node_current_status'][node_name]['status'] != new_status:
                        data['node_current_status'][node_name]['status'] = new_status
                        f.seek(0)
                        json.dump(data, f, indent=4)
                        f.truncate()

    def update_current_cap_status(self, arduino_id, moisture_level):
        node_name = self.__find_node_name(arduino_id)
        if node_name:
            with self.lock:
                with open(self.json_file, 'r+') as f:
                    data = json.load(f)
                    if data['node_current_status'][node_name]['current_cap_status'] != moisture_level:
                        data['node_current_status'][node_name]['current_cap_status'] = moisture_level
                        f.seek(0)
                        json.dump(data, f, indent=4)
                        f.truncate()

    def __find_node_name(self, arduino_id):
        for node_id, node_info in self.data['node_detail'].items():
            if node_id == arduino_id:
                return node_info['node_name']
        return None


if __name__ == "__main__":
    # Example usage
    json_file = r'data\node_connection_graph.json'
    updater = NodeStatusUpdater(json_file)

    # Update node status
    updater.update_node_status("1", True)

    # Update current_cap_status
    updater.update_current_cap_status("1", -1)
