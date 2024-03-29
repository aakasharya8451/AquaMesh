from pymongo.server_api import ServerApi
from pymongo.mongo_client import MongoClient
import time
import threading
import json
from collections import deque
from confluent_kafka import Consumer,  KafkaException, KafkaError
import sys
from dotenv import load_dotenv
import os

load_dotenv()

# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.get_node_status import GetNodeStatus
from utils.shortest_route import ShortestRoute
from utils.node_api_call import NodeAPICaller
from utils.node_status_updater import NodeStatusUpdater

class MongoDBManager:
    def __init__(self):
        # self.client = MongoClient(uri, server_api=ServerApi(version='1'))
        self.client = MongoClient(
            os.getenv("MONGODB_ATLAS_URI"), server_api=ServerApi(version='1'))

    def connect_and_create_if_not_exists(self, database_name, collection_name):
        self.db = self.client[database_name]
        self.collection = self.db[collection_name]

        # Check if the database exists, if not, create it
        if database_name not in self.client.list_database_names():
            print(f"Database '{database_name}' does not exist. Creating...")
            self.db = self.client[database_name]

        # Check if the collection exists, if not, create it
        if collection_name not in self.db.list_collection_names():
            print(f"Collection '{collection_name}' does not exist in database '{
                  database_name}'. Creating...")
            self.collection = self.db[collection_name]
            # Optionally, you can define indexes or other configurations here

    def insert_batch(self, batch):
        try:
            if batch:
                result = self.collection.insert_many(batch)
                print("Inserted batch of", len(batch), "messages")
        except Exception as e:
            print(e)

class InitiateShortestRoute:
    def __init__(self, json_file):
        self.low_node_queue = deque()
        self.lock = threading.Lock()
        self.process_thread = threading.Thread(target=self.process)
        self.process_thread.daemon = True
        self.process_thread.start()
        self.shortest_route = ShortestRoute(json_file)
        self.api_caller = NodeAPICaller(json_file)
        self.getter = GetNodeStatus(json_file)

    def add_new_low_node(self, arduino_id):
        with self.lock:
            if arduino_id not in self.low_node_queue:
                self.low_node_queue.append(arduino_id)

    def remove_processed_node(self, arduino_id):
        with self.lock:
            if arduino_id in self.low_node_queue:
                self.low_node_queue.remove(arduino_id)

    def get_next_low_node(self):
        with self.lock:
            if self.low_node_queue:
                return self.low_node_queue.popleft()
            else:
                return None

    def process(self):
        while True:
            try:
                arduino_id = self.get_next_low_node()
                if arduino_id is not None:
                    # Do some work here with arduino_id
                    print(f"Processing Arduino ID: {arduino_id}")
                    # time.sleep(30)  # Simulating some work
                    # get_shortest_path()
                    # while True:
                    #     print(f"{arduino_id} status is {self.getter.get_status(arduino_id)}")
                    #     nodes_in_shortest_path = self.shortest_route.get_shortest_route(
                    #         arduino_id)
                    #     if self.getter.get_status(arduino_id) == True:
                    #         break
                    # print(f"{arduino_id} status is {self.getter.get_status(arduino_id)}")
                    nodes_in_shortest_path = self.shortest_route.get_shortest_route(
                        arduino_id)
                    print(nodes_in_shortest_path)
                    source_removed_nodes_in_shortest_path = nodes_in_shortest_path[1::]
                    print(source_removed_nodes_in_shortest_path)
                    arduino_ids_of_nodes_in_shortest_path = self.shortest_route.get_arduino_ids_from_node_name(
                        source_removed_nodes_in_shortest_path)
                    print(arduino_ids_of_nodes_in_shortest_path)
                    for ids in arduino_ids_of_nodes_in_shortest_path:
                        self.api_caller.call_api(ids, "on")
                    while True:
                        if self.getter.get_current_cap_status(arduino_id) == 1:
                            break
                    print(f"{arduino_id} status is {self.getter.get_status(arduino_id)}, {
                        self.getter.get_current_cap_status(arduino_id)}")
                    self.remove_processed_node(arduino_id)
                    for ids in arduino_ids_of_nodes_in_shortest_path:
                        self.api_caller.call_api(ids, "off")
                    print(f"Success :: Processed Arduino ID: {arduino_id}")
            except Exception as e:
                print(f"Error occurred: {e}. Restarting thread...")
                self.process_thread = threading.Thread(target=self.process)
                self.process_thread.daemon = True
                self.process_thread.start()
                continue


class ArduinoNodeTracker:
    def __init__(self, json_file):
        self.node_status = {}  # Dictionary to store last seen time for each node
        self.moisture_levels = {}  # Dictionary to store moisture levels for each node
        self.removed_node = []
        self.lock = threading.Lock()  # Lock for synchronization
        self.updater = NodeStatusUpdater(json_file)
        self.api_caller = NodeAPICaller(json_file)
        self.provide_path = InitiateShortestRoute(json_file)

    def update_node_status(self, arduino_id):
        """Update the last seen time for the given Arduino ID."""
        with self.lock:
            if arduino_id not in self.node_status or arduino_id in self.removed_node:
                # print(f"first appearance {arduino_id}")
                # Set the led color Red when first appearance encountered
                self.api_caller.call_api(arduino_id, "off")
                if arduino_id in self.removed_node:
                    self.removed_node.remove(arduino_id)
            self.node_status[arduino_id] = time.time()

    def update_moisture_level(self, arduino_id, moisture_level):
        """Update the moisture level for the given Arduino ID."""
        with self.lock:
            self.moisture_levels[arduino_id] = moisture_level

    def check_node_status(self):
        """Check the status and moisture level of Arduino nodes."""
        while True:
            current_time = time.time()
            with self.lock:
                for arduino_id, last_seen_time in self.node_status.items():
                    if current_time - last_seen_time > 5:  # If not seen for a minute
                        # print(f"Arduino ID: {arduino_id} - False")
                        # Update node status
                        self.updater.update_node_status(arduino_id, False)
                        self.removed_node.append(arduino_id)
                    else:
                        # print(f"Arduino ID: {arduino_id} - True")
                        # Update node status
                        self.updater.update_node_status(arduino_id, True)
                    if arduino_id in self.moisture_levels:
                        moisture_level = self.moisture_levels[arduino_id]
                        if moisture_level >= 800:
                            # print(f"Moisture Level: Low -1 ({moisture_level})")
                            # Update current_cap_status
                            self.updater.update_current_cap_status(
                                arduino_id, -1)
                            self.provide_path.add_new_low_node(arduino_id)
                        elif moisture_level >= 400:
                            # print(f"Moisture Level: Mid 0 ({moisture_level})")
                            # Update current_cap_status
                            self.updater.update_current_cap_status(
                                arduino_id, 0)
                        else:
                            # print(f"Moisture Level: High 1 ({moisture_level})")
                            # Update current_cap_status
                            self.updater.update_current_cap_status(
                                arduino_id, 1)
            time.sleep(5)  # Check status every 30 seconds


# Example usage
json_file = r'data\node_connection_graph.json'
tracker = ArduinoNodeTracker(json_file)

mongo_manager = MongoDBManager()
mongo_manager.connect_and_create_if_not_exists('test', 'temp')

# Kafka broker configurations
kafka_cluster_server = f"{os.getenv('KAFKA_CLUSTER_SERVER_IP')}:{
    os.getenv('KAFKA_CLUSTER_SERVER_PORT')}"
topic_name = "iot"


def consume_messages(group_id):
    """Consume messages from a Kafka topic."""
    print(f"Consumer from Group {group_id} subscribed to topic {topic_name}")

    # Consumer configuration
    consumer_config = {
        'bootstrap.servers': kafka_cluster_server,
        'group.id': group_id,
        'auto.offset.reset': 'latest',  # Start consuming from the latest message
    }

    # Create Consumer instance
    consumer = Consumer(consumer_config)

    # Subscribe to topic(s)
    consumer.subscribe([topic_name])

    batch_size = 1000  # Number of messages to batch
    # Maximum time interval (in seconds) to wait before inserting a batch
    batch_timeout = 10
    batch = []


    join_time = time.time()
    last_batch_time = time.time()
    try:
        while True:
            # Poll for messages
            msg = consumer.poll(timeout=-1)

            if msg is None:
                continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    raise KafkaException(msg.error())

            message_timestamp = msg.timestamp()[1] / 1000.0
            if message_timestamp > join_time:
                # Process the message
                raw_message = msg.value().decode('utf-8')
                message = json.loads(raw_message)
                # print(f"Received message: {oy}, {type(oy)}")

                # Update last seen time for the Arduino ID
                arduino_id = str(message.get('arduinoID'))
                tracker.update_node_status(arduino_id)

                # Update moisture level for the Arduino ID
                moisture_level = int(message.get('moisture'))
                tracker.update_moisture_level(arduino_id, moisture_level)

                try:
                    batch.append(message)
                    if len(batch) >= batch_size or time.time() - last_batch_time >= batch_timeout:
                        mongo_manager.insert_batch(batch)
                        batch = []
                        last_batch_time = time.time()
                except Exception as e:
                    print(e)     

    except KeyboardInterrupt:
        # Close the consumer on interrupt
        consumer.close()
        print("Consumer stopped due to keyboard interrupt.")

    except Exception as e:
        print(f"An error occurred: {e}")
        consumer.close()
        raise


# Start a thread to periodically check the status and moisture level of Arduino nodes
status_checker_thread = threading.Thread(target=tracker.check_node_status)
status_checker_thread.daemon = True  # Daemonize the thread
status_checker_thread.start()

# Example usage
# group_id = input("Enter Group ID: ").strip().lower()
consume_messages("group_id")
