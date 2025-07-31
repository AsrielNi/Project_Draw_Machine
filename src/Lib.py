import os
import json
from threading import Thread

def load_json_file(json_path: str, encoding: str = "UTF-8") -> dict:
    if os.path.isfile(json_path) == False:
        raise FileNotFoundError()
    else:
        json_dict: dict
        with open(json_path, encoding=encoding) as read_file:
            all_content = read_file.read()
            json_dict = json.loads(all_content)
        return json_dict

def save_json_file(data: dict, json_path: str, encoding: str = "UTF-8") -> None:
    with open(json_path, mode="w", encoding=encoding) as save_file:
        covert_data = json.dumps(data, indent=4, ensure_ascii=False)
        save_file.write(covert_data)


def wrap_func_to_thread(func, *args, **kwargs):
    def wrap():
        wrap_thread = Thread(target=func, args=args, kwargs=kwargs, daemon=True)
        wrap_thread.start()
    return wrap

def wrap_func(func, *args, **kwargs):
    def wrap():
        func(*args, **kwargs)
    return wrap
