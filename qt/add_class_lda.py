# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\USER\PycharmProjects\domanic\qt\add_class_lda.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_add_class_lda(object):
    def setupUi(self, add_class_lda):
        add_class_lda.setObjectName("add_class_lda")
        add_class_lda.resize(400, 171)
        self.lineEdit_title = QtWidgets.QLineEdit(add_class_lda)
        self.lineEdit_title.setGeometry(QtCore.QRect(20, 30, 361, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lineEdit_title.setFont(font)
        self.lineEdit_title.setObjectName("lineEdit_title")
        self.label = QtWidgets.QLabel(add_class_lda)
        self.label.setGeometry(QtCore.QRect(20, 10, 351, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.buttonBox = QtWidgets.QDialogButtonBox(add_class_lda)
        self.buttonBox.setGeometry(QtCore.QRect(220, 130, 159, 31))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.buttonBox.setFont(font)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.lineEdit_category = QtWidgets.QLineEdit(add_class_lda)
        self.lineEdit_category.setGeometry(QtCore.QRect(20, 90, 361, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lineEdit_category.setFont(font)
        self.lineEdit_category.setObjectName("lineEdit_category")
        self.label_2 = QtWidgets.QLabel(add_class_lda)
        self.label_2.setGeometry(QtCore.QRect(20, 70, 351, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")

        self.retranslateUi(add_class_lda)
        QtCore.QMetaObject.connectSlotsByName(add_class_lda)

    def retranslateUi(self, add_class_lda):
        _translate = QtCore.QCoreApplication.translate
        add_class_lda.setWindowTitle(_translate("add_class_lda", "Добавить модель LDA"))
        self.label.setText(_translate("add_class_lda", "Название модели:"))
        self.label_2.setText(_translate("add_class_lda", "Названия категорий, через \";\" без пробелов:"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    add_class_lda = QtWidgets.QWidget()
    ui = Ui_add_class_lda()
    ui.setupUi(add_class_lda)
    add_class_lda.show()
    sys.exit(app.exec_())
