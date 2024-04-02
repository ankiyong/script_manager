
from datetime import datetime

def print_step(stage_name, msg):
    print(f"[{datetime.now()}] [{stage_name}] {msg} ")