chunk_size = 2048
files_folder = '../files/'


def read_file(file_name):
    f = open(files_folder + file_name, 'rb')   # Read file as binary
    raw_data = f.read()
    f.close()

    # Calculate number of chunks based on file_size
    num_of_chunks = len(raw_data) / chunk_size
    if len(raw_data) % num_of_chunks:
        num_of_chunks += 1

    # Create list containing pieces of raw_data using chunk_size to divide it
    chunks = []
    for i in range(0, len(raw_data) + 1, chunk_size):
        chunks.append(raw_data[i: i + chunk_size])

    return raw_data, chunks


def write_file(file_name, chunks):
    f = open(file_name, 'wb')   # Write file as binary
    # Write chunk by chunk into the binary file
    for c in chunks:
        f.write(c)

    f.close()


# data, data_chunks = read_file('voyage.mp4')
# print "File size: {}, Total chunks: {}".format(len(data), len(data_chunks))
#
# write_file('test.mp4', data_chunks)
