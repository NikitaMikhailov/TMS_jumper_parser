# Multi-Sensor Serial Logger

A lightweight system for logging data from multiple microcontrollers connected over USB serial ports (Linux/Raspberry Pi or Windows), buffering it into per-sensor CSV files, and validating the recorded data quality.

Each sensor streams lines in the format `<SENSOR_ID> <TIMESTAMP> <X> <Y> <Z>`. Incoming lines are routed to the right sensor by ID, buffered in memory, and flushed to disk on a timer — so the pipeline keeps up with several high-rate serial streams at once without blocking on I/O.

## 📦 Contents

- `main.py` — starts the logger
- `port_handler.py` — reads data from serial (COM) ports
- `dispatcher.py` — routes incoming lines to per-sensor queues
- `csv_writer.py` — buffers and writes data to CSV
- `validate_csv.py` — checks recorded data quality and builds an Excel report
- `config/config.yaml` — system configuration

## ⚙️ Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Edit `config/config.yaml`:

```yaml
logging:                     # logging settings
  log_file: logs/system.log
  log_level: INFO
  max_bytes: 1048576
  backup_count: 5

serial:
  ports:                     # ports to read sensor data from
    - COM4 #/dev/ttyACM0
    - COM6 #/dev/ttyACM1
    - COM9 #/dev/ttyACM2
    - COM7 #/dev/ttyACM3
  baudrate: 250000            # port speed
  read_timeout: 0.1           # port read timeout

sensors:
  ids: [HR, HL, FR, FL]       # sensor identifiers expected at the start of each incoming line

buffer:
  flush_interval_ms: 1000     # interval for flushing the buffer to a file (ms)
  buffer_size: 100            # read buffer size (number of records)

output:
  directory: data             # directory for measurement data and validation reports

validator_settings:
  delta_min: 9                 # minimum time between samples
  delta_max: 11                 # maximum time between samples
  valid_block_length: 20        # how many consecutive in-range samples count as a "valid period"
```

`serial.ports` and `sensors.ids` are independent lists: ports are just where data comes from, while each incoming line is routed by the sensor ID at its start. Adjust `sensors.ids` to match however many sensors your setup actually has.

3. Start collecting data:

Run from the project root:

```bash
python main.py
```

Stop the run with `CTRL+C` when the experiment is finished.

4. Validate the results and generate an Excel report:

```bash
python validate_csv.py
```
