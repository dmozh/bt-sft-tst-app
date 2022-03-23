def handle_parse(string):
    _params = {}
    _parsed_key_values = []
    for elem in string.split("&"):
        _parsed_key_values.append(tuple(elem.split('=')))

    _params.update(_parsed_key_values)
    return _params