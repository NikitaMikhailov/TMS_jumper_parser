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
    # Load configuration and logger
    config = ConfigManager.get_instance()
    logger = LoggerSingleton.get_instance()

    serial_ports = config.get("serial.ports", [])
    if not serial_ports:
        logger.error("No serial ports defined in config.")
        sys.exit(1)

    sensor_ids = config.get("sensors.ids", [])
    if not sensor_ids:
        logger.error("No sensor IDs defined in config.")
        sys.exit(1)

    # Queues
    raw_data_queue = Queue()
    sensor_queues = {sid: Queue() for sid in sensor_ids}

    # Start port readers
    handlers = []
    for port in serial_ports:
        handler = PortHandler(port, raw_data_queue)
        handler.start()
        handlers.append(handler)

    # Start the dispatcher
    dispatcher = Dispatcher(raw_data_queue, sensor_queues)
    dispatcher.start()

    # Start CSV writers
    writers = {}
    for sid in sensor_ids:
        writer = CSVWriter(sid, sensor_queues[sid])
        writer.start()
        writers[sid] = writer

    logger.info("System started. Press Ctrl+C to stop.")

    # Wait for Ctrl+C and shut down gracefully
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

        # Wait for threads to finish
        for handler in handlers:
            handler.join()
        dispatcher.join()
        for writer in writers.values():
            writer.join()

        logger.info("All threads stopped. Exiting.")

if __name__ == "__main__":
    main()
