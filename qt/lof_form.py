# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt/lof_form.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_LOF_form(object):
    def setupUi(self, LOF_form):
        LOF_form.setObjectName("LOF_form")
        LOF_form.resize(1200, 600)
        self.gridLayout_5 = QtWidgets.QGridLayout(LOF_form)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.label_title_window = QtWidgets.QLabel(LOF_form)
        self.label_title_window.setAutoFillBackground(False)
        self.label_title_window.setAlignment(QtCore.Qt.AlignCenter)
        self.label_title_window.setObjectName("label_title_window")
        self.gridLayout_5.addWidget(self.label_title_window, 0, 0, 1, 1)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout_pca = QtWidgets.QHBoxLayout()
        self.horizontalLayout_pca.setObjectName("horizontalLayout_pca")
        self.gridLayout.addLayout(self.horizontalLayout_pca, 0, 1, 1, 1)
        self.horizontalLayout_bar = QtWidgets.QHBoxLayout()
        self.horizontalLayout_bar.setObjectName("horizontalLayout_bar")
        self.gridLayout.addLayout(self.horizontalLayout_bar, 0, 2, 1, 1)
        self.horizontalLayout_tsne = QtWidgets.QHBoxLayout()
        self.horizontalLayout_tsne.setObjectName("horizontalLayout_tsne")
        self.gridLayout.addLayout(self.horizontalLayout_tsne, 0, 0, 1, 1)
        self.gridLayout_5.addLayout(self.gridLayout, 1, 0, 1, 1)
        self.gridLayout_4 = QtWidgets.QGridLayout()
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.listWidget_samples = QtWidgets.QListWidget(LOF_form)
        self.listWidget_samples.setObjectName("listWidget_samples")
        self.gridLayout_4.addWidget(self.listWidget_samples, 0, 0, 1, 1)
        self.listWidget_features = QtWidgets.QListWidget(LOF_form)
        self.listWidget_features.setObjectName("listWidget_features")
        self.gridLayout_4.addWidget(self.listWidget_features, 0, 1, 1, 1)
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.spinBox_lof_n = QtWidgets.QSpinBox(LOF_form)
        self.spinBox_lof_n.setObjectName("spinBox_lof_n")
        self.gridLayout_3.addWidget(self.spinBox_lof_n, 0, 0, 1, 1)
        self.doubleSpinBox_label = QtWidgets.QDoubleSpinBox(LOF_form)
        self.doubleSpinBox_label.setObjectName("doubleSpinBox_label")
        self.gridLayout_3.addWidget(self.doubleSpinBox_label, 1, 0, 1, 1)
        self.checkBox_samples = QtWidgets.QCheckBox(LOF_form)
        self.checkBox_samples.setObjectName("checkBox_samples")
        self.gridLayout_3.addWidget(self.checkBox_samples, 2, 0, 1, 1)
        self.pushButton_8 = QtWidgets.QPushButton(LOF_form)
        self.pushButton_8.setText("")
        self.pushButton_8.setObjectName("pushButton_8")
        self.gridLayout_3.addWidget(self.pushButton_8, 3, 0, 1, 1)
        self.pushButton_6 = QtWidgets.QPushButton(LOF_form)
        self.pushButton_6.setText("")
        self.pushButton_6.setObjectName("pushButton_6")
        self.gridLayout_3.addWidget(self.pushButton_6, 4, 0, 1, 1)
        self.gridLayout_4.addLayout(self.gridLayout_3, 0, 2, 1, 1)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.pushButton_lof = QtWidgets.QPushButton(LOF_form)
        self.pushButton_lof.setObjectName("pushButton_lof")
        self.gridLayout_2.addWidget(self.pushButton_lof, 0, 0, 1, 1)
        self.pushButton_clean_lof = QtWidgets.QPushButton(LOF_form)
        self.pushButton_clean_lof.setObjectName("pushButton_clean_lof")
        self.gridLayout_2.addWidget(self.pushButton_clean_lof, 1, 0, 1, 1)
        self.pushButton_9 = QtWidgets.QPushButton(LOF_form)
        self.pushButton_9.setText("")
        self.pushButton_9.setObjectName("pushButton_9")
        self.gridLayout_2.addWidget(self.pushButton_9, 2, 0, 1, 1)
        self.pushButton_7 = QtWidgets.QPushButton(LOF_form)
        self.pushButton_7.setText("")
        self.pushButton_7.setObjectName("pushButton_7")
        self.gridLayout_2.addWidget(self.pushButton_7, 3, 0, 1, 1)
        self.pushButton_5 = QtWidgets.QPushButton(LOF_form)
        self.pushButton_5.setText("")
        self.pushButton_5.setObjectName("pushButton_5")
        self.gridLayout_2.addWidget(self.pushButton_5, 4, 0, 1, 1)
        self.gridLayout_4.addLayout(self.gridLayout_2, 0, 3, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_4.addItem(spacerItem, 0, 4, 1, 1)
        self.gridLayout_4.setColumnStretch(0, 2)
        self.gridLayout_4.setColumnStretch(1, 2)
        self.gridLayout_4.setColumnStretch(2, 1)
        self.gridLayout_4.setColumnStretch(3, 1)
        self.gridLayout_4.setColumnStretch(4, 5)
        self.gridLayout_5.addLayout(self.gridLayout_4, 2, 0, 1, 1)
        self.gridLayout_5.setRowStretch(1, 2)
        self.gridLayout_5.setRowStretch(2, 1)

        self.retranslateUi(LOF_form)
        QtCore.QMetaObject.connectSlotsByName(LOF_form)

    def retranslateUi(self, LOF_form):
        _translate = QtCore.QCoreApplication.translate
        LOF_form.setWindowTitle(_translate("LOF_form", "Поиск выбросов"))
        self.label_title_window.setText(_translate("LOF_form", "TextLabel"))
        self.checkBox_samples.setText(_translate("LOF_form", "samples"))
        self.pushButton_lof.setToolTip(_translate("LOF_form", "Пересчитать LOF"))
        self.pushButton_lof.setText(_translate("LOF_form", "LOF"))
        self.pushButton_clean_lof.setToolTip(_translate("LOF_form", "Убрать выбросы"))
        self.pushButton_clean_lof.setText(_translate("LOF_form", "Clean"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    LOF_form = QtWidgets.QWidget()
    ui = Ui_LOF_form()
    ui.setupUi(LOF_form)
    LOF_form.show()
    sys.exit(app.exec_())
