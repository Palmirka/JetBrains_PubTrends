import pprint
import csv

def log(type: str, data) -> None:
    if isinstance(data, dict):
        print(f"DEBUG INFO {type}:")
        pprint.pprint(data)
    else:
        print(f"DEBUG INFO {type}: {data}")


def save(data, csv_filepath: str) -> None:
    try:
        features, matrix = data
        with open(csv_filepath, "w") as file:
            writer = csv.writer(file)
            writer.writerow(["Document_ID"] + list(features))
            for idx, row in enumerate(matrix):
                writer.writerow([f"{idx + 1}"] + list(row))
        print(f"DEBUG INFO: Saving data to {csv_filepath} successfull")

    except Exception as e:
        print(f"DEBUG INFO: Saving data unsuccessfully ERROR: {e}")
