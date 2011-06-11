def minmax(min, max, v, default=None):
    """ensure v is >= min and <= max"""
    if v is None:
        v = default
    if v < min:
        return min
    elif v > max:
        return max
    else:
        return v

def dict_to_string_keys(d):
    result = {}
    for k,v in d.iteritems():
        result[str(k)] = v
    return result