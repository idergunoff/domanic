# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt/choose_calculated_data.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ChooseCalcData(object):
    def setupUi(self, ChooseCalcData):
        ChooseCalcData.setObjectName("ChooseCalcData")
        ChooseCalcData.resize(400, 400)
        self.gridLayout = QtWidgets.QGridLayout(ChooseCalcData)
        self.gridLayout.setObjectName("gridLayout")
        self.pushButton_ok = QtWidgets.QPushButton(ChooseCalcData)
        self.pushButton_ok.setStyleSheet("background-color: rgb(191, 255, 191);")
        self.pushButton_ok.setObjectName("pushButton_ok")
        self.gridLayout.addWidget(self.pushButton_ok, 2, 0, 1, 1)
        self.listWidget = QtWidgets.QListWidget(ChooseCalcData)
        self.listWidget.setObjectName("listWidget")
        self.gridLayout.addWidget(self.listWidget, 1, 0, 1, 1)
        self.label = QtWidgets.QLabel(ChooseCalcData)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.retranslateUi(ChooseCalcData)
        QtCore.QMetaObject.connectSlotsByName(ChooseCalcData)

    def retranslateUi(self, ChooseCalcData):
        _translate = QtCore.QCoreApplication.translate
        ChooseCalcData.setWindowTitle(_translate("ChooseCalcData", "Выбор расчетных данных"))
        self.pushButton_ok.setText(_translate("ChooseCalcData", "ОК"))
        self.label.setText(_translate("ChooseCalcData", "TextLabel"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ChooseCalcData = QtWidgets.QWidget()
    ui = Ui_ChooseCalcData()
    ui.setupUi(ChooseCalcData)
    ChooseCalcData.show()
    sys.exit(app.exec_())
