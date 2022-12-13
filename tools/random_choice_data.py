def get_random_choice_for_type(dtype: str):
    if dtype == 'INTEGER':
        pass
    elif 'VARCHAR' in dtype:
        pass
    else:
        raise TypeError('DType not supported for random choice')