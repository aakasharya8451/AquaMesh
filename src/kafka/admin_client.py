from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka.admin import KafkaException
from dotenv import load_dotenv
import os

load_dotenv()


# Kafka broker configurations
kafka_cluster_server = f"{os.getenv('KAFKA_CLUSTER_SERVER_IP')}:{
    os.getenv('KAFKA_CLUSTER_SERVER_PORT')}"

def create_topic(topic_name, num_partitions, replication_factor):
    """Create a new Kafka topic."""
    admin_client = AdminClient({'bootstrap.servers': kafka_cluster_server})
    print("Creating a new Kafka topic:", topic_name)
    topic = NewTopic(topic_name, num_partitions, replication_factor)
    fs = admin_client.create_topics([topic])

    # Wait for each operation to finish and handle errors gracefully.
    for topic_name, future in fs.items():
        try:
            future.result()  # This will raise an exception if creation failed
            print(f"Kafka topic '{topic_name}' created successfully.")
        except KafkaException as e:
            error_msg = e.args[0].str()
            print(f"Failed to create Kafka topic '{topic_name}': {error_msg}")
    print("Admin Client terminated.")


topic_name = "iot"
num_partitions = 6
replication_factor = 1  # Set according to your setup

create_topic(topic_name, num_partitions, replication_factor)