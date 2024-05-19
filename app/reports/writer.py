import json
import os


def writer(report_data:dict, output_dir:str) -> None:
    """Write standard style report to matching files"""
    for filepath, data in report_data.items():
        dir:str = os.path.dirname(filepath)
        file:str =os.path.basename(filepath)
        path:str = f'{output_dir}{dir}'
        os.makedirs(path, exist_ok=True)

        with open(f'{path}/{file}', 'w+') as f:
            if type(data) is not str:
                json.dump(data, f, sort_keys=True, indent=2, default=str)
            else:
                f.write(data)
