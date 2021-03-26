def strToBool(txt):
    if txt == 'True':
        return True
    elif txt == 'False':
        return False
    elif txt == 'true':
        return True
    elif txt == 'false':
        return False
    elif txt == '0':
        return False
    elif txt == '1':
        return True
    else:
        return None
