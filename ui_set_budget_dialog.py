# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'set_budget_dialog.ui'
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

class Ui_SetBudgetDialog(object):
    def setupUi(self, SetBudgetDialog):
        if not SetBudgetDialog.objectName():
            SetBudgetDialog.setObjectName(u"SetBudgetDialog")
        SetBudgetDialog.resize(300, 120)
        SetBudgetDialog.setMinimumSize(QSize(300, 0))
        self.form_layout = QFormLayout(SetBudgetDialog)
        self.form_layout.setObjectName(u"form_layout")
        self.cat_label = QLabel(SetBudgetDialog)
        self.cat_label.setObjectName(u"cat_label")

        self.form_layout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.cat_label)

        self.cat_combo = QComboBox(SetBudgetDialog)
        self.cat_combo.setObjectName(u"cat_combo")
        self.cat_combo.setEditable(True)

        self.form_layout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.cat_combo)

        self.limit_label = QLabel(SetBudgetDialog)
        self.limit_label.setObjectName(u"limit_label")

        self.form_layout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.limit_label)

        self.limit_edit = QLineEdit(SetBudgetDialog)
        self.limit_edit.setObjectName(u"limit_edit")

        self.form_layout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.limit_edit)

        self.button_box = QDialogButtonBox(SetBudgetDialog)
        self.button_box.setObjectName(u"button_box")
        self.button_box.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.form_layout.setWidget(2, QFormLayout.ItemRole.SpanningRole, self.button_box)


        self.retranslateUi(SetBudgetDialog)

        QMetaObject.connectSlotsByName(SetBudgetDialog)
    # setupUi

    def retranslateUi(self, SetBudgetDialog):
        SetBudgetDialog.setWindowTitle(QCoreApplication.translate("SetBudgetDialog", u"\u8bbe\u7f6e\u9884\u7b97", None))
        self.cat_label.setText(QCoreApplication.translate("SetBudgetDialog", u"\u7c7b\u522b:", None))
        self.limit_label.setText(QCoreApplication.translate("SetBudgetDialog", u"\u6708\u5ea6\u9650\u989d:", None))
    # retranslateUi

