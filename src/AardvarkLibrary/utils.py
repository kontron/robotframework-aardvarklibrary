from robot.utils import normalizing

def _int_any_base(i, base=0):
    try:
        return int(i, base)
    except TypeError:
        return i

def int_any_base(i, base=0):
    try:
        return _int_any_base(i, base)
    except ValueError:
        raise RuntimeError('Could not parse integer "%s"' % i)

def list_any_input(data):
    """Convert any input to list.

    data can be:
     basestring: '0x10 0x22 0xab' => [16, 32, 171]
     list:        [16, 32, 171] => [16, 32, 171]
     value:       16 => [16]
     value:       0x10 => [16]
    """
    if isinstance(data, str):
        data = [_int_any_base(d) for d in data.split(' ')]
    elif isinstance(data, tuple):
        data = [d for d in data]
    elif isinstance(data, list):
        data = data
    else:
        data = [_int_any_base(data)]
    return data
