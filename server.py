from util import *
import math
import os
import sqlite3
import sys
import codecs
import zlib
from pathlib import Path
import xmlrpc
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

# Create server
server = SimpleXMLRPCServer(('0.0.0.0', 10011), requestHandler=RequestHandler)

server.register_introspection_functions()

processing_file = {}

db = sqlite3.connect('msg.db')

c = db.cursor()

c.execute('create table if not exists msg (what text)')
db.commit()

def rpc_send_text(s):
    print(s)
    c.execute('insert into msg values (?)', [s])
    db.commit()
    return True
server.register_function(rpc_send_text)

@server.register_function
def rpc_send_file_open(fn):
    fn = './files/' + fn
    print("file: ", fn)
    f = open(fn, 'wb+')
    processing_file[fn] = f
    return True

@server.register_function
def rpc_send_file_content(fn, b):
    fn = './files/' + fn
    f = processing_file[fn]
    f.write(fileunzip(b))
    return True

@server.register_function
def rpc_send_file_close(fn):
    fn = './files/' + fn
    processing_file[fn].close()
    return True


@server.register_function
def get_update():
    p = Path('./files')
    c.execute('select * from msg')
    msgs = [strzip(msg[0]) for msg in c.fetchall()]
    files = [strzip(f.name) for f in p.iterdir() if not f.is_dir()]
    return msgs, files

@server.register_function
def download_file(fn, loc):
    fn = './files/' + fn
    with open(fn, 'rb') as f:
        f.seek(loc)
        return xmlrpc.client.Binary(filezip(f.read(CHUNCK_SIZE)))

@server.register_function
def get_file_size(fn):
    fn = './files/' + fn
    return os.path.getsize(fn)

@server.register_function
def clear_all():
    os.system('rm -rf ./files')
    os.system('rm -rf msg.db')

# Run the server's main loop
server.serve_forever()
db.close()
