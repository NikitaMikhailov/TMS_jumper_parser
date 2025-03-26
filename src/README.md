# Sensor Logger System

Система записи данных с 4 микроконтроллеров по USB (Raspberry Pi/Linux), сохранение в CSV-файлы, валидация качества данных.

## 📦 Состав

- `main.py` — запуск логгера
- `port_handler.py` — чтение данных с COM-портов
- `dispatcher.py` — распределение по очередям
- `csv_writer.py` — буферизация и запись в CSV
- `validate_csv.py` — проверка качества данных
- `config/config.yaml` — конфигурация системы

## ⚙️ Настройка

1. Установите зависимости:

```bash
pip install pyserial pandas pyyaml xlsxwriter
```

2. Настройте `config/config.yaml`:

Перейдите в папку `config` и отредактируйте файл `config.yaml`
```yaml
logging:                  # настройка логирования
  log_file: logs/system.log
  log_level: INFO
  max_bytes: 1048576
  backup_count: 5

serial:
  ports:                  # порты для считывания данных с датчиков
    - COM4 #/dev/ttyACM0
    - COM6 #/dev/ttyACM1
    - COM9 #/dev/ttyACM2
    - COM7 #/dev/ttyACM3
  baudrate: 250000        # скорость порта
  read_timeout: 0.1       # таймаут на считывание портов

buffer:
  flush_interval_ms: 1000 # интервал записи из буфера в файл (мс)
  buffer_size: 100        # размер буфера считывания (количество записей)

output:
  directory: data         # директория хранения данных измерений и результатов валидации

validator_settings:
  delta_min: 9            # минимальное время между отсчётами
  delta_max: 11           # максимальное время между отсчётами
  valid_block_length: 20  # сколько подряд точек считать "валидным периодом"
```

3. Запустите сбор данных:

Перейдите в корневую папку проекта src/ и запустите скрипт:
```bash
python main.py
```
После завершения эксперимента остановить скрипт CTRL+C.

4. Автоматически проверьте результаты и сформируйте Excel-файлы отчетов.

```bash
python validate_csv.py
```



