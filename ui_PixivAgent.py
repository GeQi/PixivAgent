# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'PixivAgent.ui'
#
# Created: Fri Jan 30 21:48:02 2015
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

class Ui_main(object):
    def setupUi(self, main):
        main.setObjectName(_fromUtf8("main"))
        main.resize(386, 97)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(main.sizePolicy().hasHeightForWidth())
        main.setSizePolicy(sizePolicy)
        main.setMinimumSize(QtCore.QSize(0, 0))
        main.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.verticalLayout = QtGui.QVBoxLayout(main)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(main)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.id = QtGui.QLineEdit(main)
        self.id.setInputMethodHints(QtCore.Qt.ImhDigitsOnly)
        self.id.setPlaceholderText(_fromUtf8(""))
        self.id.setObjectName(_fromUtf8("id"))
        self.horizontalLayout.addWidget(self.id)
        self.line = QtGui.QFrame(main)
        self.line.setFrameShape(QtGui.QFrame.VLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.horizontalLayout.addWidget(self.line)
        self.label_3 = QtGui.QLabel(main)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.horizontalLayout.addWidget(self.label_3)
        self.amount = QtGui.QSpinBox(main)
        self.amount.setButtonSymbols(QtGui.QAbstractSpinBox.UpDownArrows)
        self.amount.setMinimum(1)
        self.amount.setMaximum(999)
        self.amount.setObjectName(_fromUtf8("amount"))
        self.horizontalLayout.addWidget(self.amount)
        self.label_4 = QtGui.QLabel(main)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.horizontalLayout.addWidget(self.label_4)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label_2 = QtGui.QLabel(main)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout_2.addWidget(self.label_2)
        self.dir = QtGui.QLineEdit(main)
        self.dir.setPlaceholderText(_fromUtf8(""))
        self.dir.setObjectName(_fromUtf8("dir"))
        self.horizontalLayout_2.addWidget(self.dir)
        self.btn_dir = QtGui.QToolButton(main)
        self.btn_dir.setObjectName(_fromUtf8("btn_dir"))
        self.horizontalLayout_2.addWidget(self.btn_dir)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.btn = QtGui.QPushButton(main)
        self.btn.setObjectName(_fromUtf8("btn"))
        self.verticalLayout.addWidget(self.btn)
        self.label.setBuddy(self.id)
        self.label_3.setBuddy(self.amount)
        self.label_4.setBuddy(self.amount)
        self.label_2.setBuddy(self.dir)

        self.retranslateUi(main)
        QtCore.QMetaObject.connectSlotsByName(main)
        main.setTabOrder(self.id, self.amount)
        main.setTabOrder(self.amount, self.dir)
        main.setTabOrder(self.dir, self.btn_dir)
        main.setTabOrder(self.btn_dir, self.btn)

    def retranslateUi(self, main):
        main.setWindowTitle(_translate("main", "Pixiv Agent", None))
        self.label.setText(_translate("main", "画师ID:", None))
        self.label_3.setText(_translate("main", "前", None))
        self.label_4.setText(_translate("main", "项", None))
        self.label_2.setText(_translate("main", "下载目录:", None))
        self.btn_dir.setText(_translate("main", "...", None))
        self.btn.setText(_translate("main", "登录", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    main = QtGui.QDialog()
    ui = Ui_main()
    ui.setupUi(main)
    main.show()
    sys.exit(app.exec_())

