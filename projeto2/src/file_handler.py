# Get's the projeto2.pdf, reads it as binary
f = open('../docs/projeto2.pdf', 'rb')
data = f.read()
f.close()


file_size = len(data)
print 'File size: {}'.format(file_size)

# Calculate number of chunks based on file_size
chunk_size = 1024
total_chunks = file_size / chunk_size
if file_size % total_chunks:
    total_chunks += 1

print 'Total chunks: {}'.format(total_chunks)

# Writes a copy of original file writing chunk by chunk
f = open('test.pdf', 'wb')
for i in range(0, file_size + 1, chunk_size):
    f.write(data[i: i + chunk_size])

f.close()
