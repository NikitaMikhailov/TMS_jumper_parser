import os
import pandas as pd
from glob import glob
from collections import defaultdict
from config_loader import ConfigManager

config = ConfigManager.get_instance()

settings = config.get("validator_settings", {})

REQUIRED_SENSORS = {"HR", "HL", "FR", "FL"}

DELTA_MIN = settings.get("delta_min", [])
DELTA_MAX = settings.get("delta_max", [])
VALID_BLOCK_LENGTH = settings.get("valid_block_length", [])

def extract_sensor_and_stamp(filename):
    base = os.path.basename(filename)
    name = base.replace(".csv", "")
    try:
        sensor, timestamp = name.split("_", 1)
        return sensor, timestamp
    except ValueError:
        return None, None

def detect_valid_periods(timestamps):
    deltas = timestamps.diff().fillna(0)
    valid_mask = (deltas >= DELTA_MIN) & (deltas <= DELTA_MAX)
    streak = 0
    result = []
    for ok in valid_mask:
        if ok:
            streak += 1
        else:
            streak = 0
        result.append(streak >= VALID_BLOCK_LENGTH)
    return result

def validate_sensor_file(sensor_id, file_path):
    try:
        df = pd.read_csv(file_path, sep=r"\s+", header=None, engine="python")
    except pd.errors.EmptyDataError:
        return pd.DataFrame(), False, "Файл пуст"

    if df.empty or len(df) < 2:
        return df, False, "Недостаточно данных"

    df.columns = ["Sensor", "Timestamp", "X", "Y", "Z"]
    df["Timestamp"] = df["Timestamp"].astype(int)
    df["ValidPeriod"] = detect_valid_periods(df["Timestamp"])
    out_of_range = ((df["Timestamp"].diff() < DELTA_MIN) | (df["Timestamp"].diff() > DELTA_MAX)).sum()
    if out_of_range:
        return df, False, f"Найдены отклонения по времени: {out_of_range}, всего строк: {len(df)}"
    return df, True, f"ОК, отклонений по времени: {out_of_range}, всего строк: {len(df)}"

def validate_group(timestamp, files_dict, folder_path="data"):
    print(f"\n🧪 Валидация эксперимента: {timestamp}")
    result_dfs = {}
    row_counts = {}

    # Проверка каждого сенсора
    for sensor in REQUIRED_SENSORS:
        path = files_dict.get(sensor)
        if not path:
            print(f"{sensor}: ❌ - Файл отсутствует")
            result_dfs[sensor] = pd.DataFrame()
            continue

        df, valid, msg = validate_sensor_file(sensor, path)
        print(f"{sensor}: {'✅' if valid else '❌'} - {msg}")
        result_dfs[sensor] = df
        row_counts[sensor] = len(df)

    # Проверка наличия всех сенсоров
    missing = {s for s in REQUIRED_SENSORS if result_dfs[s].empty}
    if missing:
        print(f"❌ Нет данных от сенсоров: {', '.join(missing)}")

    # Проверка количества строк (только если все сенсоры есть)
    if not missing:
        lengths = list(row_counts.values())
        max_len = max(lengths)
        min_len = min(lengths)
        diff = max_len - min_len
        allowed_diff = max(4, (max_len // 6000) * 4)
        if diff > allowed_diff:
            print(f"❌ Разница в количестве строк превышает допустимую: {diff} > {allowed_diff}")
        else:
            print(f"✅ Кол-во строк в пределах нормы (разница {diff} ≤ {allowed_diff})")

    # Сохранение Excel
    output_name = f"experiment_{timestamp}.xlsx"
    output_path = os.path.join(folder_path, output_name)
    with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
        for sensor, df in result_dfs.items():
            if df.empty:
                pd.DataFrame(columns=["Sensor", "Timestamp", "X", "Y", "Z", "ValidPeriod"]).to_excel(writer, sheet_name=sensor, index=False)
            else:
                df.to_excel(writer, sheet_name=sensor, index=False)

    print(f"📄 Отчёт сохранён: {output_path}")

def validate_all(folder_path="data"):
    files = glob(os.path.join(folder_path, "*.csv"))
    grouped = defaultdict(dict)

    for file in files:
        sensor, timestamp = extract_sensor_and_stamp(file)
        if sensor in REQUIRED_SENSORS and timestamp:
            grouped[timestamp][sensor] = file

    if not grouped:
        print("❌ Не найдено подходящих файлов для анализа.")
        return

    for timestamp, files_dict in grouped.items():
        validate_group(timestamp, files_dict, folder_path)

if __name__ == "__main__":
    validate_all()
