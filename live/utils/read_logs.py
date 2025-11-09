import ast
import re

from dataclasses import dataclass
from datetime import datetime

from ib_async import *


@dataclass(init=False)
class IbkrLogItem:
    time: datetime
    name: str
    level: str
    raw_message: str
    
    message_type: str = None
    message_obj: str = None
    
    
    def __init__(self, raw_line: str):
        line = raw_line.split(" ")
        self.time = datetime.strptime(line[0] + line[1], "%Y-%m-%d%H:%M:%S,%f")
        self.name = line[2]
        self.level = line[3]
        self.raw_message = " ".join(line[4:])
        
        raw_msg_splt = self.raw_message.split(" ")
        maybe_obj = " ".join(raw_msg_splt[1:]) if len(raw_msg_splt) > 1 else ""
        match = re.match(r"(\w+)\((.*)\)", maybe_obj)
        #print(match)
        #print(maybe_obj)
        # if match:
        #     class_name, args_str = match.groups()
        #     kwargs = ast.literal_eval("dict(" + args_str + ")")
        #     self.message_obj = globals()[class_name](**kwargs)
        #     self.message_type = raw_msg_splt[0]


class IbkrLogReader: 
    def __init__(self, file_path: str):
        self.log_items = []
        with open(file_path) as log_file:
            self.log_items = [IbkrLogItem(line) for line in log_file.readlines()]
            

if __name__ == "__main__":
    
    reader = IbkrLogReader("logs/log_2025-11-06_07-32-50.txt")
    #print(reader.log_items)