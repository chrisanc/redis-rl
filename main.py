import threading
import json
import time
import random
import redis
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

data = dict()
lock = threading.Lock()

# Define the publisher thread
class Publisher(threading.Thread):
    def __init__(self):
        super().__init__()
        self.redis = redis.Redis(host='192.168.68.110', port=6379, db=0)

    def run(self):
        """
        Defines the thread content to execute
        """
        global data
        data = {"temperature": 20}
        while True:
            json_datos = json.dumps({"T_target": data["temperature"]})
            print(f"El publisher acaba de enviar: {json_datos}")
            self.redis.publish('canal1_1', json_datos)
            time.sleep(30)


# Define the Subscriber thread...
class Subscriber(threading.Thread):
    def __init__(self):
        super().__init__()
        # redis://192.168.68.110:6379
        self.redis = redis.Redis(host='192.168.68.110', port=6379, db=0, decode_responses=True)
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe("canal1_2")

    
    def run(self):
        """
        Defines the thread content to execute
        """
        global data
        while True:
            message = self.pubsub.get_message()
            if message == None or type(message["data"]) == int:
                continue

            print(f"El suscriptor recibio un mensaje")
            # Parse the received object to JSON (map)
            data = json.loads(message["data"])
            print(data)

            # Sleep the thread for 2 seconds
            time.sleep(1)


class Charts(threading.Thread):
    def __init__(self):
        super().__init__()
        self.x = []
        self.y = []
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot(self.x, self.y, lw=2, marker="o")
        self.ax.set_xlabel("Tiempo")
        self.ax.set_ylabel("Temperatura")
        self.ax.grid(visible=True)

    def init_chart(self):
        self.line.set_data([], [])
        return self.line,

    def update(self, frame):
        with lock:
            temp = data  # tu variable global

        self.x.append(len(self.x))  # o timestamp
        self.y.append(temp["temperature"])

        # Ventana deslizante
        self.ax.set_xlim(max(0, len(self.x) - 100), len(self.x))
        self.ax.set_ylim(min(self.y) - 2, max(self.y) + 2)

        self.line.set_data(self.x, self.y)
        return self.line,

    def run(self):
        self.ani = animation.FuncAnimation(
            self.fig,
            self.update,
            init_func=self.init_chart,
            interval=1000,  # cada 1 segundo
            blit=False       # False si cambias los límites del eje
        )
    

if __name__ == "__main__":
    # Instanciate the Publisher
    pub = Publisher()
    # Instanciate the Subscriber
    sub = Subscriber()
    chart = Charts()

    # Start the thread execution
    pub.start()
    sub.start()
    chart.start()

    # Wait 'till they're done
    plt.show()
    pub.join()
    sub.join()
    chart.join()