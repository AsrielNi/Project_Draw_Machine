import os
import json


def load_json_file(json_path: str, encoding: str = "cp950") -> dict:
    if os.path.isfile(json_path) == False:
        raise FileNotFoundError()
    else:
        json_dict: dict
        with open(json_path, encoding=encoding) as read_file:
            all_content = read_file.read()
            json_dict = json.loads(all_content)
        return json_dict

def save_json_file(data: dict, json_path: str, encoding: str = "cp950") -> None:
    with open(json_path, mode="w", encoding=encoding) as save_file:
        covert_data = json.dumps(data, indent=4)
        save_file.write(covert_data)
