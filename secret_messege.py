HEAD = "\u0000"
TAIL = "\u1111"

class record:
    def __init__(self):
        pass
    
    recType = 0
    dataLen = 0
    data = 0

class messege:
    def __init__(self):
        pass

    head = format(ord(HEAD), '016b')
    tail = format(ord(TAIL), '016b')

    records = [record]
