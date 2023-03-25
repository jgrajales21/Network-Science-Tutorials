def sock_read(sock):
    bin_data = b''
    while True:
        bin_data += sock.recv(4096)
        try:
            bin_data.decode('utf-8').index('DONE')
            break
        except ValueError:
            pass

    return bin_data[:-4].decode('utf-8')

def sock_write(sock, str_data):
    str_data = str_data + 'DONE'
    bin_data = str_data.encode('utf-8')
    sock.send(bin_data)
