"""
This module is responsible for creating packages that will be used to help with the reliability of UDP.


"""

import file_handler
import checksum
import struct


TYPE_ACK = 0
TYPE_DATA = 1


class ReliableUDP(object):

    __flag_syn = None
    __flag_fin = None
    __seq_number = None
    __payload = None
    __package_type = None
    __checksum = None

    def __init__(self, _from_string=None, _seq_number=None, _payload=None, _package_type=None):

        if _from_string is not None:
            #print _from_string[0:60]
            __lines = str(_from_string).split("\n", 5)
            self.package_type = int(__lines[0].split()[1])
            self.flag_syn = bool(__lines[1].split()[1] == 'True')
            self.flag_fin = bool(__lines[2].split()[1] == 'True')
            self.seq_number = __lines[3].split()[1]
            _checksum = int(__lines[4].split()[1])
            self.payload = __lines[5]

            if checksum.verify(self.payload, _checksum) is False:
                print "Packet is corrupt"

        """ Binario
        if _from_string is not None:
            _payload_size = str(len(_from_string) - 14)
            (self.package_type, self.flag_syn, self.flag_fin,
             self.seq_number, _checksum, self.payload) = struct.unpack('!h??QH'+_payload_size+'s', _from_string)

            if checksum.verify(self.payload, _checksum) is False:
                print "Packet is corrupt"
        """

        if _seq_number is not None:
            self.seq_number = _seq_number
        if _payload is not None:
            self.payload = _payload
        if _package_type is not None:
            self.package_type = _package_type


    @property
    def flag_syn(self):
        return self.__flag_syn

    @flag_syn.setter
    def flag_syn(self, _value):
        if type(_value) is bool or _value is None:
            self.__flag_syn = _value
        else:
            self.__flag_syn = None
            print "ReliableUDP: could not set flag_syn."

    @property
    def flag_fin(self):
        return self.__flag_fin

    @flag_fin.setter
    def flag_fin(self, _value):
        if type(_value) is bool or _value is None:
            self.__flag_fin = _value
        else:
            self.__flag_fin = None
            print "ReliableUDP: could not set flag_fin."

    @property
    def seq_number(self):
        return self.__seq_number

    @seq_number.setter
    def seq_number(self, _seq_number):
        if _seq_number < 0:
            print "ReliableUDP: invalid sequence number."
        else:
            self.__seq_number = _seq_number

    @property
    def package_type(self):
        return self.__package_type

    @package_type.setter
    def package_type(self, _type):
        if _type in [TYPE_DATA, TYPE_ACK]:
            self.__package_type = _type
        else:
            print "ReliableUDP: package type invalid."

    @property
    def payload(self):
        return self.__payload

    @payload.setter
    def payload(self, _payload):
        self.__payload = _payload
        self.checksum = _payload

    @property
    def checksum(self):
        return self.__checksum

    @checksum.setter
    def checksum(self, _data):
        if _data is not None:
            self.__checksum = checksum.compute(_data)

    def to_string(self):
        return "TYPE {}\nSYN {}\nFIN {}\nSEQ_NUMBER {}\nCHECKSUM {}\n{}"\
                   .format(self.package_type, self.flag_syn, self.flag_fin,
                           self.seq_number, self.checksum, self.payload)

    """ Binario
    def pack(self):
        _payload_size = str(len(self.payload))
        return struct.pack('!h??QH'+_payload_size+'s', self.package_type, self.flag_syn, self.flag_fin,
                           self.seq_number, self.checksum, self.payload)
    """


def create_ack(_package_number):
    _payload = 'ACK ' + str(_package_number)
    return ReliableUDP(_seq_number=_package_number, _payload=_payload, _package_type=TYPE_ACK)


def create_data(_seq_number, _payload, _flag_syn=False, _flag_fin=False):
    _package = ReliableUDP(_seq_number=_seq_number, _payload=_payload, _package_type=TYPE_DATA)
    _package.flag_syn = _flag_syn
    _package.flag_fin = _flag_fin
    return _package


def pack_chunks(_chunks):
    _packs = [create_data(_chunks.index(_payload), _payload) for _payload in _chunks]
    _packs[0].flag_syn = True
    _packs[-1].flag_fin = True
    return _packs


""" DEBUG ONLY """
# raw_data, chunks = file_handler.read_file("../../files/dc_ufscar.jpg")
# chunks = ["this\nis\na\nbig", "is", "sparta"]
# pack = pack_chunks(chunks)
#
# for p in pack:
#     print p.to_string()
#     print "SEQ_NUMBER: {} SYN: {} FIN: {} CHECKSUM: {}".format(p.seq_number, p.flag_syn, p.flag_fin, p.checksum)

# for p in pack:
#     n_p = ReliableUDP(p.to_string())
#     print "TYPE {}\nSYN {}\nFIN {}\nSEQ_NUMBER {}\nCHECKSUM {}\n{}"\
#         .format(n_p.package_type, n_p.flag_syn, n_p.flag_fin,
#                 n_p.seq_number, n_p.checksum, n_p.payload)
