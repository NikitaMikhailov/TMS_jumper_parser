# main.py

import sys
import time
from queue import Queue

from config_loader import ConfigManager
from logger import LoggerSingleton
from port_handler import PortHandler
from dispatcher import Dispatcher
from csv_writer import CSVWriter


def main():
    # Загрузка конфигурации и логгера
    config = ConfigManager.get_instance()
    logger = LoggerSingleton.get_instance()

    serial_ports = config.get("serial.ports", [])
    if not serial_ports:
        logger.error("No serial ports defined in config.")
        sys.exit(1)

    # Очереди
    raw_data_queue = Queue()
    sensor_ids = ["HR", "HL", "FR", "FL"]
    sensor_queues = {sid: Queue() for sid in sensor_ids}

    # Запуск портов
    handlers = []
    for port in serial_ports:
        handler = PortHandler(port, raw_data_queue)
        handler.start()
        handlers.append(handler)

    # Запуск диспетчера
    dispatcher = Dispatcher(raw_data_queue, sensor_queues)
    dispatcher.start()

    # Запуск писателей CSV
    writers = {}
    for sid in sensor_ids:
        writer = CSVWriter(sid, sensor_queues[sid])
        writer.start()
        writers[sid] = writer

    logger.info("System started. Press Ctrl+C to stop.")

    # Ожидание Ctrl+C и graceful shutdown
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutdown initiated. Stopping threads...")

        for handler in handlers:
            handler.stop()
        dispatcher.stop()
        for writer in writers.values():
            writer.stop()

        # Подождать завершения
        for handler in handlers:
            handler.join()
        dispatcher.join()
        for writer in writers.values():
            writer.join()

        logger.info("All threads stopped. Exiting.")

if __name__ == "__main__":
    main()
