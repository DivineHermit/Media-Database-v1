# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_mdb_entries_converter.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Converter(object):
    def setupUi(self, Converter):
        Converter.setObjectName("Converter")
        Converter.setWindowModality(QtCore.Qt.WindowModal)
        Converter.resize(600, 95)
        Converter.setMinimumSize(QtCore.QSize(500, 95))
        Converter.setMaximumSize(QtCore.QSize(800, 95))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        Converter.setFont(font)
        self.centralwidget = QtWidgets.QWidget(Converter)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.hl_convert_options_layout = QtWidgets.QHBoxLayout()
        self.hl_convert_options_layout.setSpacing(5)
        self.hl_convert_options_layout.setObjectName("hl_convert_options_layout")
        self.cb_old_values = QtWidgets.QComboBox(self.centralwidget)
        self.cb_old_values.setCurrentText("")
        self.cb_old_values.setInsertPolicy(QtWidgets.QComboBox.InsertAlphabetically)
        self.cb_old_values.setObjectName("cb_old_values")
        self.hl_convert_options_layout.addWidget(self.cb_old_values)
        self.lbl_to = QtWidgets.QLabel(self.centralwidget)
        self.lbl_to.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_to.setObjectName("lbl_to")
        self.hl_convert_options_layout.addWidget(self.lbl_to)
        self.cb_new_values = QtWidgets.QComboBox(self.centralwidget)
        self.cb_new_values.setInsertPolicy(QtWidgets.QComboBox.InsertAlphabetically)
        self.cb_new_values.setObjectName("cb_new_values")
        self.hl_convert_options_layout.addWidget(self.cb_new_values)
        self.hl_convert_options_layout.setStretch(0, 1)
        self.hl_convert_options_layout.setStretch(2, 1)
        self.verticalLayout.addLayout(self.hl_convert_options_layout)
        self.hl_buttons = QtWidgets.QHBoxLayout()
        self.hl_buttons.setSpacing(5)
        self.hl_buttons.setObjectName("hl_buttons")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.hl_buttons.addItem(spacerItem)
        self.btn_ok = QtWidgets.QPushButton(self.centralwidget)
        self.btn_ok.setObjectName("btn_ok")
        self.hl_buttons.addWidget(self.btn_ok)
        self.btn_cancel = QtWidgets.QPushButton(self.centralwidget)
        self.btn_cancel.setObjectName("btn_cancel")
        self.hl_buttons.addWidget(self.btn_cancel)
        self.hl_buttons.setStretch(0, 1)
        self.verticalLayout.addLayout(self.hl_buttons)
        Converter.setCentralWidget(self.centralwidget)

        self.retranslateUi(Converter)
        QtCore.QMetaObject.connectSlotsByName(Converter)

    def retranslateUi(self, Converter):
        _translate = QtCore.QCoreApplication.translate
        Converter.setWindowTitle(_translate("Converter", "MainWindow"))
        self.cb_old_values.setToolTip(_translate("Converter", "Old value."))
        self.cb_old_values.setStatusTip(_translate("Converter", "Old value."))
        self.cb_old_values.setWhatsThis(_translate("Converter", "Old value."))
        self.lbl_to.setText(_translate("Converter", "Convert to >>"))
        self.cb_new_values.setToolTip(_translate("Converter", "New value."))
        self.cb_new_values.setStatusTip(_translate("Converter", "New value."))
        self.cb_new_values.setWhatsThis(_translate("Converter", "New value."))
        self.btn_ok.setText(_translate("Converter", "&Ok"))
        self.btn_ok.setShortcut(_translate("Converter", "Alt+O"))
        self.btn_cancel.setText(_translate("Converter", "&Cancel"))
        self.btn_cancel.setShortcut(_translate("Converter", "Esc"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Converter = QtWidgets.QMainWindow()
    ui = Ui_Converter()
    ui.setupUi(Converter)
    Converter.show()
    sys.exit(app.exec_())

