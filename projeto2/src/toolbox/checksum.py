class Checksum:

    @staticmethod
    def __create(data):
        size = len(data)
        remainder = size % 2
        payload = data
        if remainder == 1 :
            payload += '\0'
        payload = list(payload)
        checksum = 0
        size = (size + remainder)/2
        max_int = 2**16 - 1
        while size > 0:
            size -= 1
            m = ord(payload[2*size]) << 8
            n = ord(payload[2*size+1])
            checksum = (checksum + (m | n)) & max_int;
        return checksum

    @staticmethod
    def compute(data):
        c = Checksum.__create(data)
        return ((~c) + 1) & (2**16 - 1)

    @staticmethod
    def verify(data, checksum):
        c = Checksum.__create(data)
        return ((c + checksum) & (2**16 - 1)) == 0


d = raw_input()
c = Checksum.compute(d)
print Checksum.verify(d, c+1)
print Checksum.verify(d, c)

