# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\USER\PycharmProjects\domanic\qt\compare_table_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_CompareTableInt(object):
    def setupUi(self, CompareTableInt):
        CompareTableInt.setObjectName("CompareTableInt")
        CompareTableInt.resize(974, 528)
        self.gridLayout = QtWidgets.QGridLayout(CompareTableInt)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(CompareTableInt)
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.tableWidget = QtWidgets.QTableWidget(CompareTableInt)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.gridLayout.addWidget(self.tableWidget, 1, 0, 1, 1)
        self.pushButton_save = QtWidgets.QPushButton(CompareTableInt)
        self.pushButton_save.setStyleSheet("background-color: rgb(191, 255, 191);")
        self.pushButton_save.setObjectName("pushButton_save")
        self.gridLayout.addWidget(self.pushButton_save, 2, 0, 1, 1)

        self.retranslateUi(CompareTableInt)
        QtCore.QMetaObject.connectSlotsByName(CompareTableInt)

    def retranslateUi(self, CompareTableInt):
        _translate = QtCore.QCoreApplication.translate
        CompareTableInt.setWindowTitle(_translate("CompareTableInt", "Compare Interval"))
        self.label.setText(_translate("CompareTableInt", "Статистические параметры для сравнения интервалов"))
        self.pushButton_save.setText(_translate("CompareTableInt", "Сохранить"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    CompareTableInt = QtWidgets.QWidget()
    ui = Ui_CompareTableInt()
    ui.setupUi(CompareTableInt)
    CompareTableInt.show()
    sys.exit(app.exec_())
