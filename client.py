from util import *
import math
import sys
import codecs
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QClipboard,QTextCursor
import xmlrpc.client
import pathlib


# Subclass QMainWindow to customise your application's main window
class Window(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)

        self.setWindowTitle("My Awesome App")

        self.__init_data()

        # set layout
        self.__layout()

        # self.add_result_label()
        # self.add_left_comboBox()
        # self.add_plus_label()
        # self.add_right_comboBox()

        self.msg_l = []
        self.file_l = []
        self.add_open_file_button()
        self.add_send_file_button()
        self.add_text_edit()
        self.add_send_text_button()
        self.add_msg_list()
        self.add_file_list()
        self.add_labels()
        self.add_clearall()
        self.add_status_box()
        self.server_addr = 'http://pi:10011'
        self.add_reflush_button()
        self.set_stretch()
        self.grid.setRowStretch(0, 10)
        try:
            self.proxy = xmlrpc.client.ServerProxy(self.server_addr)
            print(self.proxy.system.listMethods())
            self.log("Connected to " + self.server_addr) 
        except ConnectionError:
            self.log("Error connecting to " + self.server_addr) 

        # self.add_matplotlib_figure()

    def set_stretch(self):
        self.msg_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.file_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.text_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.send_text_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.reflush_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.status_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def log(self, msg):
        self.status_box.moveCursor(QTextCursor.End)
        self.status_box.insertPlainText(msg + '\n')
        self.status_box.moveCursor(QTextCursor.End)

    def __init_data(self):
        '''
        init global datas for the app.
        '''
        pass

    def __layout(self):
        '''
        set the global layout of the window.
        window.setLayout is not valid, so add a middleware `main_frame`
        '''
        self.grid = QGridLayout()
        self.grid.setSpacing(20)
        main_frame = QWidget()
        main_frame.setLayout(self.grid)
        self.setCentralWidget(main_frame)    

    def do_send_file(self):
        fn = self.open_file_button.text()
        self.log("Sending " + self.open_file_button.text())
        p = pathlib.Path(fn)
        self.proxy.rpc_send_file_open(p.name)
        sent_bytes_cnt = 0
        with open(fn , 'rb') as f:
            b = f.read(CHUNCK_SIZE)
            while b:
                self.proxy.rpc_send_file_content(p.name, xmlrpc.client.Binary(filezip(b)))
                sent_bytes_cnt += len(b)
                self.log('Sent ' + str(sent_bytes_cnt))
                b = f.read(CHUNCK_SIZE)
        self.proxy.rpc_send_file_close(p.name)
        self.log("Sent " + self.open_file_button.text())

    def add_send_file_button(self):
        self.send_file_button = QPushButton('send file', parent=self)
        self.grid.addWidget(self.send_file_button, 0, 1)
        self.send_file_button.clicked.connect(self.do_send_file)
    

    def show_open_file_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, 'QFileDialog.getOpenFileName()', '', 'All Files (*);;CSV (*.csv)', options=options)
        if fileName:
            self.open_file_button.setText(fileName)

    def add_open_file_button(self):
        self.open_file_button = QPushButton('open file', parent=self)
        self.grid.addWidget(self.open_file_button, 0, 0)
        self.open_file_button.clicked.connect(self.show_open_file_dialog)
    
    def add_text_edit(self):
        self.text_box = QPlainTextEdit(self)
        self.grid.addWidget(self.text_box, 1, 0, 3, 1)

    def add_send_text_button(self):
        self.send_text_button = QPushButton('send text', parent = self)
        self.grid.addWidget(self.send_text_button, 1, 1)
        self.send_text_button.clicked.connect(self.do_send_text)
    
    def do_send_text(self):
        self.log("Sending text")
        self.proxy.rpc_send_text(self.text_box.toPlainText())
        self.log("Sent text")

    def on_msg_clicked(self, item):
        QGuiApplication.clipboard().setText(item.text())
        self.log('msg copied to clipboard')

    def add_msg_list(self):
        self.msg_list = QListWidget(self)
        self.grid.addWidget(self.msg_list, 1, 2, 3, 1)
        self.msg_list.itemDoubleClicked.connect(self.on_msg_clicked)
        # self.msg_list.setFixedWidth(100)
    
    def add_labels(self):
        self.grid.addWidget(QLabel('msg list', parent=self), 0, 2)
        self.grid.addWidget(QLabel('file list', parent=self), 0, 3)

    def add_status_box(self):
        self.status_box = QPlainTextEdit(self)
        self.grid.addWidget(self.status_box, 4, 0, 1, 4)

    def add_reflush_button(self):
        self.reflush_button = QPushButton('REFLUSH!', parent=self)
        self.grid.addWidget(self.reflush_button, 2, 1)
        self.reflush_button.clicked.connect(self.do_reflush)
    
    def do_reflush(self):
        msg_l, file_l = self.proxy.get_update()
        self.msg_l = [strunzip(msg) for msg in msg_l]
        self.file_l = [strunzip(f) for f in file_l]
        self.msg_list.clear()
        self.file_list.clear()
        for msg in self.msg_l:
            self.msg_list.addItem(msg)
        for f in self.file_l:
            self.file_list.addItem(f)

    def add_file_list(self):
        self.file_list = QListWidget(self)
        self.file_list.itemDoubleClicked.connect(self.on_file_clicked)
        self.grid.addWidget(self.file_list, 1, 3, 3, 1)
    
    def on_file_clicked(self, item):
        fn = item.text()
        flen = self.proxy.get_file_size(fn)
        self.log('Start downloading ' + fn + '(' + str(flen) + ')')
        f = open(fn, 'wb+')
        for i in range(math.ceil(flen/CHUNCK_SIZE)):
            b = self.proxy.download_file(fn, i * CHUNCK_SIZE)
            f.write(fileunzip(b))
            self.log(fn + ': downloaded ' + str(i * CHUNCK_SIZE) + '(' + str(i * CHUNCK_SIZE / flen) + '%)' )
        f.close()
        self.log(fn + ': downloaded ' + str(flen) + '(100%)')
    
    def add_clearall(self):
        self.clear_all_button = QPushButton('CLEAR REMOTE!!!')
        self.grid.addWidget(self.clear_all_button,3,1)
        self.clear_all_button.clicked.connect(self.do_clear_all)
    
    def do_clear_all(self):
        self.proxy.clear_all()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    try:
        app.exec_()
    except Exception:
        pass
