from confluent_kafka import Producer
from confluent_kafka.cimpl import KafkaException
from dotenv import load_dotenv
import os

load_dotenv()


# Kafka broker configurations
kafka_cluster_server = f"{os.getenv('KAFKA_CLUSTER_SERVER_IP')}:{
    os.getenv('KAFKA_CLUSTER_SERVER_PORT')}"

topic_name = "iot"


def delivery_report(err, msg):
    """Called once for each message produced to indicate delivery result."""
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}]')


def produce_messages(message, partition_no):
    """Produce messages to a Kafka topic."""
    producer_config = {'bootstrap.servers': kafka_cluster_server}

    try:
        # Create Producer instance
        producer = Producer(producer_config)

        # Produce message
        # producer.produce(topic_name, message.encode('utf-8'),
        #                  partition=partition_no, callback=delivery_report)
        producer.produce(topic_name, message.encode('utf-8'),
                         partition=partition_no)

        # Flush producer's message queue to ensure delivery
        producer.flush()

        # print("Message successfully sent to Kafka.")
    except KafkaException as e:
        print(f"Error producing message to Kafka: {e}")


def main():
    while True:
        message = input("Enter Message (type 'q' to quit): ")

        if message.lower() == 'q':
            break

        try:
            partition_no = 0  # Assuming messages go to partition 0
            produce_messages(message, partition_no)
        except Exception as e:
            print(f"An error occurred: {e}")

    print("Exiting message producer.")


if __name__ == "__main__":
    main()
