"""

This module is responsible for computing and verifying the checksum of a bunch of data

These methods add the capability to verify if any bit (1) has changed in the arrived packet.
It returns a number of 16-bits from a variable-sized bunch of data.

(1) Note that if an even number of bits change in the same position of different 16 bits of
data, they will not be detected.

How to use:
    To find the checksum of a bunch of binary data
    checksum = Checksum.compute(data)

    To verify if a bunch of binary data has a specific checksum
    Checksum.verify(data,checksum)

"""


class Checksum:

    @staticmethod
    def __compute(data):
        """Compute the checksum value of data

        Args:
        data (str): batch of data whose checksum value will be computed

        Returns:
        checksum (int): checksum value

        """
        size = len(data)
        remainder = size % 2
        payload = data
        # If data has an odd number of bytes, one empty byte is added to it
        if remainder == 1:
            payload += '\0'
        # Breaks payload in individual bytes to be processed
        payload = list(payload)
        # Byte array is traversed every two bytes, then half of its size
        size = (size + remainder) / 2
        checksum = 0
        # Biggest checksum value. Instantiated for improvement purposes.
        max_int = 2 ** 16 - 1
        while size > 0:
            # Byte array is traversed backwards.
            size -= 1
            # Number from 0 to 255 shifted 8 times to the left
            m = ord(payload[2 * size]) << 8
            # Number from 0 to 255
            n = ord(payload[2 * size + 1])
            # Checksum is an accumulated sum of two adjacent bytes
            # If the sum is a number greater than 2 bytes, it is rounded to 2 bytes by max_int
            checksum = (checksum + (m | n)) & max_int
        return checksum

    @staticmethod
    def compute(data):
        """Compute the checksum value of data

        Args:
        data (str): batch of data whose checksum value will be computed

        Returns:
        checksum (int): 2's complement of checksum value

        """
        c = Checksum.__compute(data)
        # The 2's complement of a binary number X is NOT(X) + 1
        return ((~c) + 1) & (2 ** 16 - 1)

    @staticmethod
    def verify(data, checksum):
        """Verify if a pair of data and checksum value is valid

        Args:
        data (str): batch of data whose checksum value will be computed
        checksum (int): checksum value

        Returns:
        True    if it is a valid pair of data and checksum
        False   otherwise

        """
        c = Checksum.__compute(data)
        # The sum of a number with its 2's complement is 0
        return ((c + checksum) & (2 ** 16 - 1)) == 0
