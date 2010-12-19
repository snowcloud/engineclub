

def dict_to_string_keys(d):
    result = {}
    for k,v in d.iteritems():
        result[str(k)] = v
    return result