from confluent_kafka import Consumer, Producer
import psycopg2
import json
import time
import logging
import random

bootstrap_servers = 'localhost:9092'
group_id = 'my_consumer_group_1'
input_topic = 'input_topic_1'
output_topic = 'output_topic_1'
final_output_topic = 'final_output_topic_1'


db_host = 'localhost'
db_port = '5432'
db_user = 'AliJokar'
db_password = 'A1234'
db_name = 'my_database'


conn = psycopg2.connect(host=db_host, port=db_port, user=db_user, password=db_password, database=db_name)
cur = conn.cursor()

def add_timestamp(data):
    data['timestamp'] = int(time.time())
    return data

def add_label(data):
    labels = ['label1', 'label2', 'label3']
    data['label'] = random.choice(labels)
    return data

def save_to_postgres(data):
    try:
        cur.execute("INSERT INTO your_table_name (id, first_name, last_name, ...) VALUES (%s, %s, %s, ...)",
                    (data['id'], data['first_name'], data['last_name'], ...))
        conn.commit()
    except Exception as e:
        print(f"An error occurred while saving data to PostgreSQL: {e}")

consumer = Consumer({
    'bootstrap.servers': bootstrap_servers,
    'group.id': group_id,
    'auto.offset.reset': 'earliest'
})
consumer.subscribe([input_topic])

producer = Producer({'bootstrap.servers': bootstrap_servers})

consumer2 = Consumer({
    'bootstrap.servers': bootstrap_servers,
    'group.id': group_id,
    'auto.offset.reset': 'earliest'
})
consumer2.subscribe([output_topic])

producer2 = Producer({'bootstrap.servers': bootstrap_servers})

consumer3 = Consumer({
    'bootstrap.servers': bootstrap_servers,
    'group.id': group_id,
    'auto.offset.reset': 'earliest'
})
consumer3.subscribe([final_output_topic])

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is not None:
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                continue

            data = json.loads(msg.value().decode('utf-8'))
            enriched_data = add_timestamp(data)

            producer.produce(output_topic, value=json.dumps(enriched_data).encode('utf-8'))

        msg2 = consumer2.poll(1.0)
        if msg2 is not None:
            if msg2.error():
                print(f"Consumer error: {msg2.error()}")
                continue

            data = json.loads(msg2.value().decode('utf-8'))
            enriched_data = add_label(data)

            producer2.produce(final_output_topic, value=json.dumps(enriched_data).encode('utf-8'))

            save_to_postgres(enriched_data)

        msg3 = consumer3.poll(1.0)
        if msg3 is not None:
            if msg3.error():
                print(f"Consumer error: {msg3.error()}")
                continue

            data = json.loads(msg3.value().decode('utf-8'))

            save_to_postgres(data)

except KeyboardInterrupt:
    pass

finally:
    consumer.close()
    consumer2.close()
    consumer3.close()
    conn.close()
