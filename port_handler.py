# port_handler.py

import threading
import serial
from queue import Queue
from logger import LoggerSingleton
from config_loader import ConfigManager


class PortHandler(threading.Thread):
    """
    Reads lines from a single serial port and pushes them into a shared queue.
    """
    def __init__(self, port: str, output_queue: Queue):
        super().__init__(daemon=True)
        self.port = port
        self.output_queue = output_queue
        self.config = ConfigManager.get_instance().get("serial")
        self.logger = LoggerSingleton.get_instance()

        self.baudrate = self.config.get("baudrate", 115200)
        self.timeout = self.config.get("read_timeout", 0.1)

        self.serial_conn = None
        self._running = threading.Event()
        self._running.set()

    def connect(self):
        try:
            self.serial_conn = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            self.logger.info(f"[{self.port}] Connected at {self.baudrate} baud.")
        except Exception as e:
            self.logger.error(f"[{self.port}] Connection failed: {e}")
            self._running.clear()

    def run(self):
        self.connect()
        if not self.serial_conn:
            return

        while self._running.is_set():
            try:
                line = self.serial_conn.readline().decode(errors='ignore').strip()
                if line:
                    self.output_queue.put(line)
            except Exception as e:
                self.logger.error(f"[{self.port}] Read error: {e}")

    def stop(self):
        self._running.clear()
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
        self.logger.info(f"[{self.port}] Disconnected.")
