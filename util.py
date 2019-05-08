import codecs
def strzip(s):
    ret = codecs.encode(bytes(s,'utf-8'), 'zlib')
    return ret

def strunzip(b):
    return str(codecs.decode(b.data, 'zlib'), 'utf-8')

def filezip(b):
    return codecs.encode(b, 'zlib')

def fileunzip(b):
    return codecs.decode(b.data, 'zlib')

CHUNCK_SIZE = 1024 * 128
PORT = 10011
