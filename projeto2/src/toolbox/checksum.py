"""

This module is responsible for computing and verifying the checksum of a bunch of data

These methods add the capability to verify if any bit (1) has changed in the arrived packet.
It returns a number of 16-bits from a variable-sized bunch of data.

(1) Note that if an even number of bits change in the same position of different 16 bits of
data, they will not be detected.

How to use:
    To find the checksum of a bunch of binary data
    checksum = compute(data)

    To verify if a bunch of binary data has a specific checksum
    verify(data,checksum)

"""

__MAX_INT = 2 ** 16 - 1
""" int: Maximum 16-bits integer number for modulo operation (via bitwise operation &)."""


def __compute(_data):
    """Compute the checksum value of data

    Args:
        _data (str): batch of data whose checksum value will be computed

    Returns:
        checksum (int): checksum value

    """
    _size = len(_data)
    _remainder = _size % 2
    _payload = _data
    # If data has an odd number of bytes, one empty byte is added to it
    if _remainder == 1:
        _payload += '\0'
    # Breaks payload in individual bytes to be processed
    _payload = list(_payload)
    # Byte array is traversed every two bytes, then half of its size
    _size = (_size + _remainder) / 2
    _checksum = 0

    while _size > 0:
        # Byte array is traversed backwards.
        _size -= 1
        # Number from 0 to 255 shifted 8 times to the left
        _byte_1 = ord(_payload[2 * _size]) << 8
        # Number from 0 to 255
        _byte_0 = ord(_payload[2 * _size + 1])
        # Checksum is an accumulated sum of two adjacent bytes
        # If the sum is a number greater than 2 bytes, it is rounded to 2 bytes by __MAX_INT
        _checksum = (_checksum + (_byte_1 | _byte_0)) & __MAX_INT
    return _checksum


def compute(_data):
    """Compute the checksum value of data

    Args:
        _data (str): batch of data whose checksum value will be computed

    Returns:
        checksum (int): 2's complement of checksum value

    """
    _c = __compute(_data)

    # The 2's complement of a binary number X is NOT(X) + 1
    return ((~_c) + 1) & __MAX_INT


def verify(_data, _checksum):
    """
    Verify if a pair of data and checksum value is valid

    Args:
        _data (str): batch of data whose checksum value will be computed
        _checksum (int): checksum value

    Returns:
        True if it is a valid pair of data and checksum,
        False otherwise

    """
    _c = __compute(_data)

    # The sum of a number with its 2's complement is 0
    return ((_c + _checksum) & __MAX_INT) == 0
