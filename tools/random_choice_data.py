import random


def get_random_choice_for_type(dtype: str):
    if dtype == "INTEGER":
        return random.choice(range(0, 100))
    elif "VARCHAR" in dtype:
        letters = "abcdefghijklmnoprsquwxyz"
        str_length = int(dtype.split("(")[1].split(")")[0])
        return "".join((random.choice(letters)) for _ in range(str_length))
    else:
        raise TypeError("DType not supported for random choice")

