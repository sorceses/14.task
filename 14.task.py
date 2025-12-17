import numpy as np
import time
import threading

class CustomQueue:
    def __init__(self):
        self.queue = []
        self.lock = threading.Lock()

    def put(self, item):
        with self.lock:
            self.queue.append(item)

    def get(self):
        with self.lock:
            if self.queue:
                return self.queue.pop(0)
            raise IndexError("get from empty queue")

tc, size, value, times = 20, 15, 2, 3
tasks_queue = CustomQueue()
results = []
results_lock = threading.Lock()

def matrix_multiply(A, B):
    return np.dot(A, B)

class Producer(threading.Thread):
    def __init__(self, consumers_count):
        super().__init__()
        self.consumers_count = consumers_count

    def run(self):
        for task_id in range(tc):
            tasks_queue.put((size + task_id, value, times))
        for _ in range(self.consumers_count):
            tasks_queue.put((None, None, None))

class Consumer(threading.Thread):
    def run(self):
        while True:
            try:
                task = tasks_queue.get()
                if task == (None, None, None):
                    break
                size, value, times = task

                matrix = np.fromfunction(lambda i, j: value ** (i + j), (size, size), dtype=int)

                if times == 0:
                    powered = np.eye(size, dtype=int)
                else:
                    powered = np.linalg.matrix_power(matrix, times)

                total = int(powered.sum())

                with results_lock:
                    results.append(total)

            except IndexError:
                time.sleep(0.001)

def main(consumers_count):
    global results
    results = []

    producer = Producer(consumers_count)
    consumers = [Consumer() for _ in range(consumers_count)]

    start_time = time.time()
    producer.start()
    for c in consumers:
        c.start()

    producer.join()
    for c in consumers:
        c.join()

    total_sum = sum(results)
    return round(time.time() - start_time, 3), total_sum

if __name__ == '__main__':
    for threads in [1, 2, 4, 8]:
        elapsed, total_sum = main(threads)
        print(f"{elapsed} seconds, {threads} threads, total sum = {total_sum}")