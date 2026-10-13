# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'add_transaction_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.11.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QApplication, QComboBox, QDialog,
    QDialogButtonBox, QFormLayout, QLabel, QLineEdit,
    QSizePolicy, QWidget)

class Ui_AddTransactionDialog(object):
    def setupUi(self, AddTransactionDialog):
        if not AddTransactionDialog.objectName():
            AddTransactionDialog.setObjectName(u"AddTransactionDialog")
        AddTransactionDialog.resize(350, 280)
        AddTransactionDialog.setMinimumSize(QSize(350, 0))
        self.form_layout = QFormLayout(AddTransactionDialog)
        self.form_layout.setObjectName(u"form_layout")
        self.date_label = QLabel(AddTransactionDialog)
        self.date_label.setObjectName(u"date_label")

        self.form_layout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.date_label)

        self.date_edit = QLineEdit(AddTransactionDialog)
        self.date_edit.setObjectName(u"date_edit")

        self.form_layout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.date_edit)

        self.amount_label = QLabel(AddTransactionDialog)
        self.amount_label.setObjectName(u"amount_label")

        self.form_layout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.amount_label)

        self.amount_edit = QLineEdit(AddTransactionDialog)
        self.amount_edit.setObjectName(u"amount_edit")

        self.form_layout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.amount_edit)

        self.type_label = QLabel(AddTransactionDialog)
        self.type_label.setObjectName(u"type_label")

        self.form_layout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.type_label)

        self.type_combo = QComboBox(AddTransactionDialog)
        self.type_combo.addItem("")
        self.type_combo.addItem("")
        self.type_combo.setObjectName(u"type_combo")

        self.form_layout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.type_combo)

        self.cat_label = QLabel(AddTransactionDialog)
        self.cat_label.setObjectName(u"cat_label")

        self.form_layout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.cat_label)

        self.cat_combo = QComboBox(AddTransactionDialog)
        self.cat_combo.setObjectName(u"cat_combo")
        self.cat_combo.setEditable(True)

        self.form_layout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.cat_combo)

        self.acc_label = QLabel(AddTransactionDialog)
        self.acc_label.setObjectName(u"acc_label")

        self.form_layout.setWidget(4, QFormLayout.ItemRole.LabelRole, self.acc_label)

        self.acc_combo = QComboBox(AddTransactionDialog)
        self.acc_combo.addItem("")
        self.acc_combo.addItem("")
        self.acc_combo.addItem("")
        self.acc_combo.addItem("")
        self.acc_combo.setObjectName(u"acc_combo")

        self.form_layout.setWidget(4, QFormLayout.ItemRole.FieldRole, self.acc_combo)

        self.note_label = QLabel(AddTransactionDialog)
        self.note_label.setObjectName(u"note_label")

        self.form_layout.setWidget(5, QFormLayout.ItemRole.LabelRole, self.note_label)

        self.note_edit = QLineEdit(AddTransactionDialog)
        self.note_edit.setObjectName(u"note_edit")

        self.form_layout.setWidget(5, QFormLayout.ItemRole.FieldRole, self.note_edit)

        self.button_box = QDialogButtonBox(AddTransactionDialog)
        self.button_box.setObjectName(u"button_box")
        self.button_box.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.form_layout.setWidget(6, QFormLayout.ItemRole.SpanningRole, self.button_box)


        self.retranslateUi(AddTransactionDialog)

        QMetaObject.connectSlotsByName(AddTransactionDialog)
    # setupUi

    def retranslateUi(self, AddTransactionDialog):
        AddTransactionDialog.setWindowTitle(QCoreApplication.translate("AddTransactionDialog", u"\u6dfb\u52a0\u4ea4\u6613", None))
        self.date_label.setText(QCoreApplication.translate("AddTransactionDialog", u"\u65e5\u671f (YYYY-MM-DD):", None))
        self.amount_label.setText(QCoreApplication.translate("AddTransactionDialog", u"\u91d1\u989d:", None))
        self.type_label.setText(QCoreApplication.translate("AddTransactionDialog", u"\u7c7b\u578b:", None))
        self.type_combo.setItemText(0, QCoreApplication.translate("AddTransactionDialog", u"\u652f\u51fa", None))
        self.type_combo.setItemText(1, QCoreApplication.translate("AddTransactionDialog", u"\u6536\u5165", None))

        self.cat_label.setText(QCoreApplication.translate("AddTransactionDialog", u"\u7c7b\u522b:", None))
        self.acc_label.setText(QCoreApplication.translate("AddTransactionDialog", u"\u8d26\u6237:", None))
        self.acc_combo.setItemText(0, QCoreApplication.translate("AddTransactionDialog", u"\u5fae\u4fe1", None))
        self.acc_combo.setItemText(1, QCoreApplication.translate("AddTransactionDialog", u"\u652f\u4ed8\u5b9d", None))
        self.acc_combo.setItemText(2, QCoreApplication.translate("AddTransactionDialog", u"\u73b0\u91d1", None))
        self.acc_combo.setItemText(3, QCoreApplication.translate("AddTransactionDialog", u"\u94f6\u884c\u5361", None))

        self.note_label.setText(QCoreApplication.translate("AddTransactionDialog", u"\u5907\u6ce8:", None))
    # retranslateUi

