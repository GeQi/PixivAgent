# -*- coding: utf-8 -*-

import os
import re
import sys
import threading
import Queue
import shutil
from zipfile import ZipFile

import requests
from lxml import html
from PIL import Image
import images2gif

import ui_PixivAgent
from PyQt4.QtCore import *
from PyQt4.QtGui import *

def get_page(session, url):
    request = session.get(url)
    doc = html.document_fromstring(request.content)
    doc.make_links_absolute("http://www.pixiv.net/")
    return doc

def iter_urls_work(session, id_user, type, num):
    for page in range(num//20+1):
        url = "http://www.pixiv.net/member_illust.php?id=%d&type=%s&p=%d" % (id_user, type, page+1)
        elems_work = get_page(session, url).find_class("image-item")

        for i, elem_work in enumerate(elems_work):
            if page*20+i+1 <= num:
                yield elem_work.find("a").get("href")
            else:
                raise StopIteration

class Work(object):
    def __init__(self, session, url_work):
        super(Work, self).__init__()
        self.session = session
        self.url = url_work
        self.page = get_page(self.session, self.url)
        self.type = self.get_type()
        self.id = self.get_id()
        self.title = self.get_title()
        self.urls_image = self.get_urls_image()

    def __len__(self):
        return len(self.urls_image)

    def get_type(self):
        elem_works_display = self.page.find_class("works_display")
        if elem_works_display[0].find_class("player"):
            return "ugoira"
        elif elem_works_display[0].find_class("manga"):
            return "manga"
        elif elem_works_display[0].find_class("multiple"):
            return "multiple"
        else:
            return "illust"

    def get_id(self):
        return re.findall(r"\d+$", self.url)[0]

    def get_title(self):
        return self.page.find_class("work-info")[0].find_class("title")[0].text

    def get_urls_image(self):
        if self.type == "ugoira":
            url = re.findall(r'http\S*?1080\.zip', html.tostring(self.page))
            return url[0].replace("\\", "")
        elif self.type == "illust":
            elems_image = self.page.find_class("original-image")
        elif self.type == "multiple":
            url = self.page.find_class("works_display")[0].find("a").get("href")
            elems_image = get_page(self.session, url).find_class("image")
        elif self.type == "manga":
            url = self.page.find_class("works_display")[0].find("a").get("href")
            elems_image = get_page(self.session, url).find_class("image")
        return [elem_image.get("data-src") for elem_image in elems_image]

    def download(self, dir, signal):
        dir_name = self.title+" "+self.id
        escaped = re.sub(r'[/\\:*?"<>|]', '-', dir_name)
        dir_download = os.path.join(dir, escaped)
        if not os.path.exists(dir_download):
            os.makedirs(dir_download)

        if self.type == "ugoira":
            dir_temp = os.path.join(dir_download, "temp")
            dir_zip = os.path.join(dir_temp, self.id+".zip")
            frames = []
            os.makedirs(dir_temp)
            url = self.urls_image
            request_zip = self.session.get(url, stream=True)
            total_length = int(request_zip.headers.get('content-length'))
            downloaded_len = 0
            with open(dir_zip, "wb") as file:
                for chunk in request_zip.iter_content(128):
                    file.write(chunk)
                    downloaded_len += len(chunk)
                    percent = int(downloaded_len*100/total_length)
                    signal.emit(self.progress, percent)
            with ZipFile(dir_zip) as file_zip:
                for image in file_zip.namelist():
                    file_zip.extract(image, dir_temp)
                    frames.append(Image.open(os.path.join(dir_temp, image)))
            images2gif.writeGif(os.path.join(dir_download, self.id+'.gif'), frames, duration=0.1)
            shutil.rmtree(dir_temp)
        else:
            for i, url in enumerate(self.urls_image):
                request_image = self.session.get(url, stream=True)
                total_length = int(request_image.headers.get('content-length'))
                downloaded_len = 0
                if self.type == "illust":
                    with open(os.path.join(dir_download, self.id+".jpg"), "wb") as file:
                        for chunk in request_image.iter_content(128):
                            file.write(chunk)
                            downloaded_len += len(chunk)
                            percent = int(downloaded_len*100/total_length)
                            signal.emit(self.progress, percent)
                elif self.type == "multiple" or "manga":
                    with open(os.path.join(dir_download, self.id+"_"+str(i+1)+r".jpg"), "wb") as file:
                        for chunk in request_image.iter_content(256):
                            file.write(chunk)
                            downloaded_len += len(chunk)
                            percent = int((i+downloaded_len/total_length)*100/len(self))
                            signal.emit(self.progress, percent)


class Main(QDialog, ui_PixivAgent.Ui_main):
    # signals:
    signal_login = pyqtSignal(bool)

    signal_analyse_start = pyqtSignal()
    signal_analyse = pyqtSignal(bool)

    signal_add_row = pyqtSignal(Work)
    signal_update_bar = pyqtSignal(QProgressBar, int)

    def __init__(self):
        QDialog.__init__(self)
        ui_PixivAgent.Ui_main.__init__(self)
        self.setupUi(self)
        self.set_login_mode(True)
        self.dir.setText(os.path.join(os.getcwd(), "Download"))

        # 初始化下载列表gui
        self.hide_table()
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setColumnWidth(0, 64)
        self.table.setColumnWidth(2, 150)
        self.table.horizontalHeader().setResizeMode(1, QHeaderView.Stretch)

        # 初始化会话
        self.session = requests.Session()
        headers = {"User-Agent": r"Chrome/40.0.2214.93",
                   "Referer": r"http://www.pixiv.net/"}
        self.session.headers.update(headers)

        # 初始化队列
        self.queue = Queue.Queue()

        # 初始化线程
        self.threads_num = 5
        self.lock = threading.Lock()
        self.event_analyse = threading.Event()
        self.event_download = threading.Event()
        self.create_thread_analyse()
        self.create_thread_download()

        # connections
        self.btn_login.clicked.connect(self.login)
        self.signal_login.connect(self.check_login)

        self.btn_dir.clicked.connect(self.show_dir)

        self.btn_analyse.clicked.connect(self.event_analyse.set)
        self.signal_analyse_start.connect(self.analyse_start)
        self.signal_analyse.connect(self.check_analyse)

        self.signal_add_row.connect(self.add_row)
        self.signal_update_bar.connect(self.update_bar)

    # 操作gui
    def set_login_mode(self, bool):
        self.widget_login.setVisible(bool)
        self.widget_analyse.setVisible(not bool)

    # 登录线程
    def login(self):
        self.enable_login_input(False)

        # 登录
        def thread_login():
            url_login = r"https://www.secure.pixiv.net/login.php"
            data = {"mode": "login",
                    "pixiv_id": str(self.email.text()),
                    "pass": str(self.password.text())}
            request_login = self.session.post(url=url_login, data=data, allow_redirects=False, verify=False)

            # 确认
            if request_login.status_code != 302:
                self.signal_login.emit(False)
            else:
                self.signal_login.emit(True)

        self.thread_login = threading.Thread(target=thread_login)
        self.thread_login.setDaemon(True)
        self.thread_login.start()

    # 操作gui
    def enable_login_input(self, bool):
        self.email.setEnabled(bool)
        self.password.setEnabled(bool)
        self.btn_login.setEnabled(bool)

    def check_login(self, bool):
        if bool:
            self.set_login_mode(False)
        else:
            self.enable_login_input(True)

    # 解析线程
    def create_thread_analyse(self):
        def thread_analyse():
            while True:
                self.event_analyse.wait()
                self.signal_analyse_start.emit()
                iter = iter_urls_work(self.session, int(self.id.text()), "", int(self.amount.text()))
                for url in iter:
                    work = Work(self.session, url)
                    with self.lock:
                        self.queue.put(work)
                    self.signal_add_row.emit(work)
                self.signal_analyse.emit(True)
                self.event_analyse.clear()

        self.thread_analyse = threading.Thread(target=thread_analyse)
        self.thread_analyse.setDaemon(True)
        self.thread_analyse.start()

    # 操作gui
    def show_table(self):
        self.btn_table.clicked.disconnect()
        self.btn_table.setText(u"收起下载列表")
        self.btn_table.clicked.connect(self.hide_table)
        self.table.setVisible(True)
        self.setMinimumHeight(297)
        self.setMaximumHeight(10800)

    def hide_table(self):
        self.btn_table.setText(u"展开下载列表")
        self.btn_table.clicked.connect(self.show_table)
        self.table.setVisible(False)
        self.setMinimumHeight(99)
        self.setMaximumHeight(99)

    def enable_analyse_input(self, bool):
        self.id.setEnabled(bool)
        self.amount.setEnabled(bool)
        self.dir.setEnabled(bool)
        self.btn_dir.setEnabled(bool)
        self.btn_analyse.setEnabled(bool)

    def analyse_start(self):
        self.enable_analyse_input(False)
        self.show_table()

    def check_analyse(self, bool):
        if bool:
            self.event_download.set()
            self.enable_analyse_input(True)
        else:
            pass     # TODO: 报错

    def add_row(self, work):
        row_num = self.table.rowCount()
        self.table.insertRow(row_num)

        item_id = QTableWidgetItem(work.id)
        item_id.setTextAlignment(Qt.AlignHCenter)
        item_id.setTextAlignment(Qt.AlignVCenter)
        self.table.setItem(row_num, 0, item_id)

        item_title = QTableWidgetItem(work.title)
        item_title.setTextAlignment(Qt.AlignHCenter)
        item_title.setTextAlignment(Qt.AlignVCenter)
        self.table.setItem(row_num, 1, item_title)

        progress = QProgressBar()
        progress.setAlignment(Qt.AlignHCenter)
        progress.setValue(0)
        work.progress = progress
        self.table.setCellWidget(row_num, 2, progress)

    def update_bar(self, progress, percent):
        progress.setValue(percent)

    # 下载线程
    def create_thread_download(self):
        def thread_download():
            while True:
                self.event_download.wait()
                while True:
                    with self.lock:
                        if not self.queue.empty():
                            work = self.queue.get()
                        else:
                            break
                    work.download(str(self.dir.text()), self.signal_update_bar)
                self.event_download.clear()

        self.threads_download = [threading.Thread(target=thread_download) for i in range(self.threads_num)]
        for thread in self.threads_download:
            thread.setDaemon(True)
            thread.start()

    # 目录选择窗口
    def show_dir(self):
        dir_download = QFileDialog.getExistingDirectory(self, u"选择下载目录")
        self.dir.setText(dir_download)


app = QApplication(sys.argv)
app.setWindowIcon(QIcon("icon.png"))
main = Main()
main.show()
app.exec_()