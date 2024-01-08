error_symbol = '.,/\'":[]{}()*%$#@!?&^`~'


def validate_fmo(value: list[str]) -> bool:
    if len(value) != 3:
        return False
    for i in value:
        for j in error_symbol:
            if j in i: return False
        if not i.isalpha(): return False
    return True