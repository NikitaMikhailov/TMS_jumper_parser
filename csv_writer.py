# csv_writer.py

import os
import threading
import time
from queue import Queue, Empty
from datetime import datetime
from logger import LoggerSingleton
from config_loader import ConfigManager


class CSVWriter(threading.Thread):
    def __init__(self, sensor_id: str, sensor_queue: Queue):
        """
        :param sensor_id: sensor identifier (e.g. HR)
        :param sensor_queue: queue of incoming lines for this sensor
        """
        super().__init__(daemon=True)
        self.sensor_id = sensor_id
        self.queue = sensor_queue
        self.logger = LoggerSingleton.get_instance()
        self.config = ConfigManager.get_instance()

        self.output_dir = self.config.get("output.directory", "data")
        os.makedirs(self.output_dir, exist_ok=True)

        self.buffer_size = self.config.get("buffer.buffer_size", 100)
        self.flush_interval = self.config.get("buffer.flush_interval_ms", 1000) / 1000.0

        # file name pattern: HR_2025-03-25_13-58-00.csv
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.file_path = os.path.join(self.output_dir, f"{self.sensor_id}_{timestamp}.csv")

        self.buffer = []
        self._running = threading.Event()
        self._running.set()

    def run(self):
        self.logger.info(f"[{self.sensor_id}] CSV writer started → {self.file_path}")
        last_flush_time = time.time()

        while self._running.is_set():
            now = time.time()

            try:
                # non-blocking get; move on if the queue is empty
                line = self.queue.get(timeout=0.01)
                self.buffer.append(line)

            except Empty:
                pass

            # flush when the buffer is full or the flush interval has elapsed
            if len(self.buffer) >= self.buffer_size or (now - last_flush_time) >= self.flush_interval:
                self.flush_to_file()
                last_flush_time = now

        # final flush on shutdown
        if self.buffer:
            self.flush_to_file()
        self.logger.info(f"[{self.sensor_id}] CSV writer stopped.")

    def flush_to_file(self):
        try:
            with open(self.file_path, "a", encoding="utf-8") as f:
                for row in self.buffer:
                    f.write(row + "\n")
            self.logger.info(f"[{self.sensor_id}] Flushed {len(self.buffer)} rows.")
            self.buffer.clear()
        except Exception as e:
            self.logger.error(f"[{self.sensor_id}] Error writing to CSV: {e}")

    def stop(self):
        self._running.clear()
