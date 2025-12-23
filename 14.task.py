import time
import threading
import queue

TC, SIZE, VALUE, TIMES = 20, 15, 2, 3

tasks_queue = queue.Queue()
results = []
results_lock = threading.Lock()

def matrix_power_pure_python(size, value, times):
    matrix = [[value ** (i + j) for j in range(size)] for i in range(size)]
    
    if times == 0:
        return size
    
    res_matrix = matrix
    for _ in range(times - 1):
        new_matrix = [[0] * size for _ in range(size)]
        for i in range(size):
            for j in range(size):
                for k in range(size):
                    new_matrix[i][j] += res_matrix[i][k] * matrix[k][j]
        res_matrix = new_matrix
    
    total = sum(sum(row) for row in res_matrix)
    return total

class Producer(threading.Thread):
    def __init__(self, consumers_count):
        super().__init__()
        self.consumers_count = consumers_count

    def run(self):
        for task_id in range(TC):
            tasks_queue.put((SIZE + task_id, VALUE, TIMES))
        
        for _ in range(self.consumers_count):
            tasks_queue.put(None)

class Consumer(threading.Thread):
    def run(self):
        while True:
            task = tasks_queue.get()
            if task is None:
                tasks_queue.task_done()
                break
                
            size, value, times = task
            total = matrix_power_pure_python(size, value, times)

            with results_lock:
                results.append(total)
            
            tasks_queue.task_done()

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
    elapsed = round(time.time() - start_time, 3)
    return elapsed, total_sum

if __name__ == '__main__':
    for threads in [1, 2, 4]:
        elapsed, total_sum = main(threads)
        print(f"Threads: {threads} | Time: {elapsed}s | Sum: {total_sum}")
