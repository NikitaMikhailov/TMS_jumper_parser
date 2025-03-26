# dispatcher.py

import threading
from queue import Queue
from logger import LoggerSingleton


class Dispatcher(threading.Thread):
    def __init__(self, input_queue: Queue, sensor_queues: dict):
        """
        :param input_queue: очередь со всеми входящими строками от всех портов
        :param sensor_queues: словарь очередей по датчикам, ключи: HR, HL, FR, FL
        """
        super().__init__(daemon=True)
        self.input_queue = input_queue
        self.sensor_queues = sensor_queues
        self.logger = LoggerSingleton.get_instance()
        self._running = threading.Event()
        self._running.set()
        self.valid_sensors = set(sensor_queues.keys())

    def run(self):
        self.logger.info("Dispatcher started.")
        while self._running.is_set():
            try:
                line = self.input_queue.get(timeout=0.1)
                parts = line.strip().split()

                if not parts:
                    continue

                if len(parts) < 5 or parts[0] not in self.sensor_queues:
                    # self.logger.warning(f"Invalid or unknown line: {line}")
                    continue
                sensor_id = parts[0]

                if sensor_id in self.sensor_queues:
                    self.sensor_queues[sensor_id].put(line)
                else:
                    self.logger.warning(f"Unknown sensor ID in line: {line}")

            except Exception as e:
                self.logger.info(f"Dispatcher error: {e}")
                continue

    def stop(self):
        self._running.clear()
        self.logger.info("Dispatcher stopped.")
