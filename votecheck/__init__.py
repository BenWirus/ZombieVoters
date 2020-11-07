import random
from time import sleep


def random_sleep(min_sec: int, max_sec: int):
    sleep(random.randint(min_sec, max_sec))
