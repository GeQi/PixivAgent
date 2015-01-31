# -*- coding: utf-8 -*-

import os
import re
import sys
import threading

import requests
from lxml import html

import ui_PixivAgent
import ui_PixivAgent_login
from PyQt4.QtCore import *
from PyQt4.QtGui import *


def get_page(session, url):
    request = session.get(url)

    doc = html.document_fromstring(request.content)
    doc.make_links_absolute(r"http://www.pixiv.net/")

    return doc


# 画师id, 作品类型 -> 作品页面url迭代器
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

    def __str__(self):
        return str(len(self))+self.type+self.id+self.title+self.url

    def __len__(self):
        return len(self.urls_image)

    def get_type(self):
        elem_works_display = self.page.find_class("works_display")
        if not elem_works_display:
            return "ugoira"
        else:
            elem_works_manga = elem_works_display[0].find_class("manga")
            if elem_works_manga:
                return "manga"
            else:
                elem_works_multiple = elem_works_display[0].find_class("multiple")
                if elem_works_multiple:
                    return "multiple"
                else:
                    return "illust"

    def get_id(self):
        return re.findall(r"\d+$", self.url)[0]      # TODO better ways?

    def get_title(self):
        return self.page.find_class("work-info")[0].find_class("title")[0].text

    def get_urls_image(self):
        if self.type == "illust":
            elems_image = self.page.find_class("original-image")
        elif self.type == "multiple":
            url = self.page.find_class("works_display")[0].find("a").get("href")      # TODO better ways?
            elems_image = get_page(self.session, url).find_class("image")
        elif self.type == "manga":
            url = self.page.find_class("works_display")[0].find("a").get("href")      # TODO better ways?
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

        for i, url in enumerate(self.urls_image):       # TODO
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
    trigger = pyqtSignal()

    def __init__(self):
        super(Main, self).__init__()
        self.setupUi(self)
        self.set_all(False)

        # 建立会话
        self.session = requests.Session()
        headers = {"User-Agent": r"Chrome/40.0.2214.93",
                   "Referer": r"http://www.pixiv.net/"}
        self.session.headers.update(headers)

        self.dir.setText(os.path.join(os.getcwd(), "Download"))

        # connections
        self.btn.clicked.connect(self.show_login)
        self.btn_dir.clicked.connect(self.show_dir)

    def set_all(self, bool):
        self.id.setEnabled(bool)
        self.amount.setEnabled(bool)
        self.dir.setEnabled(bool)
        self.btn_dir.setEnabled(bool)

    def analyse(self):
        self.set_all(False)
        self.btn.setEnabled(False)

        self.trigger.connect(self.complete)

        iter = iter_urls_work(self.session, int(self.id.text()), "", int(self.amount.text()))

        def thread_analyse():
            self.works = [Work(self.session, url) for url in iter]

        Thread(self.download, thread_analyse)

    def download(self):
        self.lock = threading.Lock()
        def thread_download():
            dir = str(self.dir.text())
            while True:
                try:
                    with self.lock:
                        work = self.works.pop()
                    work.download(dir)
                except Exception:
                    self.trigger.emit()

        threads = [threading.Thread(target=thread_download) for i in range(5)]
        for thread in threads:
            thread.start()

    def complete(self):
        self.trigger.disconnect()
        self.set_all(True)
        self.btn.setEnabled(True)

    # slots
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
        self.btn.clicked.connect(self.analyse)


class Login(QDialog, ui_PixivAgent_login.Ui_login):
    # signals
    trigger = pyqtSignal()

    def __init__(self, session, target):
        super(Login, self).__init__()
        self.setupUi(self)

        self.session = session

        # connections
        self.btn_login.clicked.connect(self.login)
        self.trigger.connect(target)

    def login(self):
        self.btn_login.setEnabled(False)
        self.email.setReadOnly(True)
        self.password.setReadOnly(True)

        # 登录
        def post():
            url_login = r"https://www.secure.pixiv.net/login.php"
            data = {"mode": "login",
                    "pixiv_id": str(self.email.text()),
                    "pass": str(self.password.text())}
            self.request_login = self.session.post(url=url_login, data=data, allow_redirects=False)

        # 确认
        def confirm():
            # if False:
            if self.request_login.status_code != 302:
                self.btn_login.setEnabled(True)
                self.email.setReadOnly(False)
                self.password.setReadOnly(False)
            else:
                self.trigger.emit()
                self.close()

        self.thread_login = Thread(confirm, post)


class Thread(QObject, threading.Thread):
    # signals
    trigger = pyqtSignal()

    def __init__(self, target, func, *a, **kw):
        threading.Thread.__init__(self)
        QObject.__init__(self)

        self.func = func
        self.a = a
        self.kw = kw

        self.trigger.connect(target)

        self.start()

    def run(self):
        self.func(*self.a, **self.kw)
        self.trigger.emit()


app = QApplication(sys.argv)
main = Main()
main.show()
app.exec_()