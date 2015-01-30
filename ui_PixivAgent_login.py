# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'PixivAgent_login.ui'
#
# Created: Thu Jan 29 17:54:13 2015
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_login(object):
    def setupUi(self, login):
        login.setObjectName(_fromUtf8("login"))
        login.resize(386, 99)
        login.setModal(True)
        self.verticalLayout = QtGui.QVBoxLayout(login)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.label = QtGui.QLabel(login)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout_3.addWidget(self.label)
        self.email = QtGui.QLineEdit(login)
        self.email.setObjectName(_fromUtf8("email"))
        self.horizontalLayout_3.addWidget(self.email)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label_2 = QtGui.QLabel(login)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout.addWidget(self.label_2)
        self.password = QtGui.QLineEdit(login)
        self.password.setEchoMode(QtGui.QLineEdit.Password)
        self.password.setObjectName(_fromUtf8("password"))
        self.horizontalLayout.addWidget(self.password)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.btn_login = QtGui.QPushButton(login)
        self.btn_login.setObjectName(_fromUtf8("btn_login"))
        self.verticalLayout.addWidget(self.btn_login)
        self.label.setBuddy(self.email)
        self.label_2.setBuddy(self.password)

        self.retranslateUi(login)
        QtCore.QMetaObject.connectSlotsByName(login)
        login.setTabOrder(self.email, self.password)
        login.setTabOrder(self.password, self.btn_login)

    def retranslateUi(self, login):
        login.setWindowTitle(_translate("login", "登录", None))
        self.label.setText(_translate("login", "E-mail:", None))
        self.label_2.setText(_translate("login", "密码:", None))
        self.btn_login.setText(_translate("login", "登录", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    login = QtGui.QDialog()
    ui = Ui_login()
    ui.setupUi(login)
    login.show()
    sys.exit(app.exec_())

