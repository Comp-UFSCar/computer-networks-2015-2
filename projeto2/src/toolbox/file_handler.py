"""

This module is responsible for reading and writing binary files.

For the communication between Receiver and Transmitter, the file must be split in smaller pieces: called here as
chunks. These chunks will be added to a list and returned to the caller of read_file function, that same list of
chunks will be used on write_file function to re-create the original binary file.

"""

CHUNK_SIZE = 2048
"""int: Chunk size to be used for splitting the file."""
FILES_FOLDER = '../files/'
"""str: Folder where files are located."""


def read_file(file_name):
    """Read a binary file and return the raw data and chunks.

    Access a binary file inside the folder FILES_FOLDER. Read the whole file buffer and store it inside raw_data.
    With the length of raw_data, the number of chunks needed is calculated and the list chunks is used to append
    each slice of the raw_data using CHUNK_SIZE as delimiter.

    Args:
        file_name (str): Name of the file that will be read. *File extension must be included.

    Returns:
        raw_data (str): File's binary data.
        chunks (List[str]): A list containing pieces of file's binary data.

    """

    try:
        f = open(FILES_FOLDER + file_name, 'rb')
    except IOError:
        return False, ""
    else:
        raw_data = f.read()  # raw_data receives all binary file buffer
        f.close()

    # Calculate number of chunks based on file_size
    num_of_chunks = len(raw_data) / CHUNK_SIZE
    if len(raw_data) % num_of_chunks:
        num_of_chunks += 1

    # Create list containing pieces of raw_data using chunk_size to divide it
    chunks = []
    for i in range(0, len(raw_data) + 1, CHUNK_SIZE):
        chunks.append(raw_data[i: i + CHUNK_SIZE])

    return raw_data, chunks


def write_file(file_name, chunks):
    """Write a binary file using list of chunks containing file's data.

    Args:
        file_name (str): Name of output file. *File extension must be included.
        chunks (List[str]): List containing pieces of file's binary data.

    """

    try:
        f = open(file_name, 'wb')
    except IOError:
        return False, ""
    else:
        # Write chunk by chunk into the binary file
        for c in chunks:
            f.write(c)
        f.close()
        return True
