# -*- coding: utf-8 -*-

import os
import re
import sys
import threading
import Queue

import requests
from lxml import html

import ui_PixivAgent
import ui_PixivAgent_login
from PyQt4.QtCore import *
from PyQt4.QtGui import *


def get_page(session, url):
    request = session.get(url)
    doc = html.document_fromstring(request.content)
    doc.make_links_absolute("http://www.pixiv.net/")
    return doc

def iter_urls_work(session, id_user, type, num):
    for page in range(num / 20 + 1):
        url = "http://www.pixiv.net/member_illust.php?id=%d&type=%s&p=%d" % (id_user, type, page+1)
        elems_work = get_page(session, url).find_class("image-item")

        for i, elem_work in enumerate(elems_work):
            yield elem_work.find("a").get("href")
            if (page * 20 + i + 1) >= num:
                break

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
        if not elem_works_display:
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
        if self.type == "illust":
            elems_image = self.page.find_class("original-image")
        elif self.type == "multiple":
            url = self.page.find_class("works_display")[0].find("a").get("href")
            elems_image = get_page(self.session, url).find_class("image")
        elif self.type == "manga":
            url = self.page.find_class("works_display")[0].find("a").get("href")
            elems_image = get_page(self.session, url).find_class("image")
        elif self.type == "ugoira":
            raise NotImplementedError        # TODO

        return [elem_image.get("data-src") for elem_image in elems_image]

    def download(self, dir):
        dir_download = os.path.join(dir, self.title+" "+self.id)
        try:
            os.makedirs(dir_download)
        except Exception:
            raise IOError

        for i, url in enumerate(self.urls_image):
            request_image = self.session.get(url)
            if self.type == "illust":
                with open(os.path.join(dir_download, self.id+".jpg"), "wb") as file:
                    file.write(request_image.content)
            elif self.type == "multiple" or "manga":
                with open(os.path.join(dir_download, self.id+"_"+str(i+1)+r".jpg"), "wb") as file:
                    file.write(request_image.content)
            elif self.type == "ugoira":
                raise NotImplementedError        # TODO


class Main(QDialog, ui_PixivAgent.Ui_main):
    # signals:
    signal_analyse_finished = pyqtSignal()

    def __init__(self):
        QDialog.__init__(self)
        ui_PixivAgent.Ui_main.__init__(self)
        self.setupUi(self)
        self.set_all(False, btn=True)
        self.dir.setText(os.path.join(os.getcwd(), "Download"))

        # 建立会话
        self.session = requests.Session()
        headers = {"User-Agent": r"Chrome/40.0.2214.93",
                   "Referer": r"http://www.pixiv.net/"}
        self.session.headers.update(headers)

        # 初始化队列
        self.queue = Queue.Queue()
        self.history = []

        # 初始化线程
        self.threads_num = 5
        self.lock = threading.Lock()
        self.event_analyse = threading.Event()
        self.event_download = threading.Event()
        self.create_thread_analyse()
        self.create_thread_download()

        # connections
        self.btn.clicked.connect(self.show_login)
        self.btn_dir.clicked.connect(self.show_dir)
        self.signal_analyse_finished.connect(self.event_download.set)
        self.signal_analyse_finished.connect(self.set_all)

    def set_all(self, bool=True, btn=True):
        self.id.setEnabled(bool)
        self.amount.setEnabled(bool)
        self.dir.setEnabled(bool)
        self.btn_dir.setEnabled(bool)
        self.btn.setEnabled(btn)

    # slots
    def create_thread_analyse(self):

        def thread_analyse():
            while True:
                self.event_analyse.wait()
                self.set_all(False, btn=False)
                iter = iter_urls_work(self.session, int(self.id.text()), "", int(self.amount.text()))
                for _url in iter:
                    work = Work(self.session, _url)
                    with self.lock:
                        if work not in self.history:
                            self.history.append(work)
                            self.queue.put(work)
                self.signal_analyse_finished.emit()
                self.event_analyse.clear()

        thread = threading.Thread(target=thread_analyse)
        thread.setDaemon(True)
        thread.start()

    def create_thread_download(self):
        def thread_download():
            while True:
                self.event_download.wait()
                print "thread awoke"
                while not self.queue.empty():
                    with self.lock:
                        work = self.queue.get()
                    work.download(str(self.dir.text()))
                self.event_download.clear()

        self.threads_download = [threading.Thread(target=thread_download) for i in range(self.threads_num)]
        for _thread in self.threads_download:
            _thread.setDaemon(True)
            _thread.start()

    def show_login(self):
        self.login = Login(self.session, self.unlock)
        self.login.show()

    def show_dir(self):
        dir = QFileDialog.getExistingDirectory(self, u"选择下载目录")
        self.dir.setText(dir)

    def unlock(self):
        self.set_all(True)
        self.btn.setText(u"下载")

        self.btn.clicked.disconnect()
        self.btn.clicked.connect(self.event_analyse.set)


class Login(QDialog, ui_PixivAgent_login.Ui_login):
    # signals
    signal_login_successed = pyqtSignal()
    signal_login_failed = pyqtSignal()

    def __init__(self, session, slot):
        QDialog.__init__(self)
        ui_PixivAgent_login.Ui_login.__init__(self)
        self.setupUi(self)

        self.session = session

        # connections
        self.btn_login.clicked.connect(self.login)
        self.signal_login_successed.connect(slot)
        self.signal_login_successed.connect(self.close)
        self.signal_login_failed.connect(self.set_all)

    def set_all(self, bool=True):
        self.btn_login.setEnabled(bool)
        self.email.setReadOnly(not bool)
        self.password.setReadOnly(not bool)

    def login(self):
        self.set_all(False)

        # 登录
        def post():
            url_login = r"https://www.secure.pixiv.net/login.php"
            data = {"mode": "login",
                    "pixiv_id": str(self.email.text()),
                    "pass": str(self.password.text())}
            request_login = self.session.post(url=url_login, data=data, allow_redirects=False, verify=False)

            # 确认
            if request_login.status_code != 302:
                self.signal_login_failed.emit()
            else:
                self.signal_login_successed.emit()

        thread = threading.Thread(target=post)
        thread.start()


app = QApplication(sys.argv)
app.setWindowIcon(QIcon("icon.png"))
main = Main()
main.show()
app.exec_()