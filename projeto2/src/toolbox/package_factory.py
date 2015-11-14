"""
This module is responsible for creating packages that will be used to help with the reliability of UDP.


"""

from enum import Enum
import file_handler


class PackageType(Enum):
    ACK = 0
    DATA = 1


class ReliableUDP(object):

    __flag_syn = None
    __flag_fin = None
    __seq_number = None
    __payload = None
    __package_type = None

    def __init__(self, _seq_number, _payload, _package_type):
        self.seq_number = _seq_number
        self.payload = _payload
        self.package_type = _package_type

    @property
    def flag_syn(self):
        return self.__flag_syn

    @flag_syn.setter
    def flag_syn(self, _value):
        if type(_value) is bool or _value is None:
            self.__flag_syn = _value
        else:
            self.__flag_syn = _value
            print "ReliableUDP: could not set flag_syn."

    @property
    def flag_fin(self):
        return self.__flag_fin

    @flag_fin.setter
    def flag_fin(self, _value):
        if type(_value) is bool or _value is None:
            self.__flag_fin = _value
        else:
            self.__flag_fin = _value
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
        if _type in PackageType:
            self.__package_type = _type
        else:
            print "ReliableUDP: package type invalid."

    @property
    def payload(self):
        return self.__payload

    @payload.setter
    def payload(self, _payload):
        self.__payload = _payload


def create_ack(_package_number):
    return ReliableUDP(_package_number, None, PackageType.ACK)


def create_data(_seq_number, _payload, _flag_syn=False, _flag_fin=False):
    _package = ReliableUDP(_seq_number, _payload, PackageType.DATA)
    _package.flag_syn = _flag_syn
    _package.flag_fin = _flag_fin
    return _package


def pack_chunks(_chunks):
    _packs = [create_data(_chunks.index(p), p) for p in _chunks]
    _packs[0].flag_syn = True
    _packs[-1].flag_fin = True
    return _packs


# raw_data, chunks = file_handler.read_file("../../files/dc_ufscar.jpg")
# pack = pack_chunks(chunks)
#
# for p in pack:
#     print "SEQ_NUMBER: {} SYN: {} FIN: {}".format(p.seq_number, p.flag_syn, p.flag_fin)
