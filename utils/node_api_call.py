import requests
import json
import threading


class NodeAPICaller:
    def __init__(self, json_file):
        self.json_file = json_file
        self.lock = threading.Lock()  # Lock for synchronization
        with open(json_file, 'r') as f:
            self.data = json.load(f)

    def __get_node_api_endpoint(self, arduino_id):
        for node_id, node_info in self.data['node_detail'].items():
            if node_id == arduino_id:
                return node_info['api_endpoint']
        return None

    def call_api(self, arduino_id, route):
        api_endpoint = self.__get_node_api_endpoint(arduino_id)
        if api_endpoint is None:
            print(f"Error: API endpoint not found for Arduino ID '{
                  arduino_id}'.")
            return None

        url = f"{api_endpoint}/{route}"
        try:
            with self.lock:
                response = requests.post(url)
            if response.ok:
                return response.text
            else:
                print(f"Error: HTTP {
                      response.status_code} - {response.reason}")
        except requests.RequestException as e:
            print(f"Error calling API: {e}")


if __name__ == "__main__":
    json_file = r'data\node_connection_graph.json'
    api_caller = NodeAPICaller(json_file)
    api_caller.call_api("1", "on")
