import threading
import json
import time
import random
import redis
import matplotlib.pyplot as plt

class Publisher(threading.Thread):
    def __init__(self):
        super().__init__()
        self.redis = redis.Redis(host='192.168.68.110', port=6379, db=0)

    def run(self):
        while True:
            temp = random.uniform(10.0, 40.0)
            json_datos = json.dumps({"T_target": temp})
            print(f"El publisher acaba de enviar: {json_datos}")
            self.redis.publish('canal1-2', json_datos)
            time.sleep(30)


class Subscriber(threading.Thread):
    def __init__(self):
        super().__init__()
        # redis://192.168.68.110:6379
        self.redis = redis.Redis(host='192.168.68.110', port=6379, db=0, decode_responses=True)
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe("canal1-1")

    
    def run(self):
        while True:
            message = self.pubsub.get_message()
            print(f"El suscriptor recibio {message}")
            time.sleep(1)
    

if __name__ == "__main__":
    # Instanciate the Publisher
    pub = Publisher()
    # Instanciate the Subscriber
    sub = Subscriber()

    pub.start()
    sub.start()

    pub.join()
    sub.join()