# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_gui.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QGroupBox, QHBoxLayout,
    QHeaderView, QLabel, QLineEdit, QMainWindow,
    QPushButton, QRadioButton, QSizePolicy, QSpacerItem,
    QStatusBar, QTabWidget, QTableWidget, QTableWidgetItem,
    QTextEdit, QToolBar, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1100, 750)
        MainWindow.setMinimumSize(QSize(900, 600))
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.central_layout = QVBoxLayout(self.centralwidget)
        self.central_layout.setObjectName(u"central_layout")
        self.central_layout.setContentsMargins(2, 2, 2, 2)
        self.tabs = QTabWidget(self.centralwidget)
        self.tabs.setObjectName(u"tabs")
        self.tab_txn = QWidget()
        self.tab_txn.setObjectName(u"tab_txn")
        self.txn_tab_layout = QVBoxLayout(self.tab_txn)
        self.txn_tab_layout.setObjectName(u"txn_tab_layout")
        self.txn_table = QTableWidget(self.tab_txn)
        if (self.txn_table.columnCount() < 6):
            self.txn_table.setColumnCount(6)
        __qtablewidgetitem = QTableWidgetItem()
        self.txn_table.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.txn_table.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.txn_table.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.txn_table.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.txn_table.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.txn_table.setHorizontalHeaderItem(5, __qtablewidgetitem5)
        self.txn_table.setObjectName(u"txn_table")
        self.txn_table.setAlternatingRowColors(True)
        self.txn_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.txn_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.txn_table.horizontalHeader().setStretchLastSection(True)

        self.txn_tab_layout.addWidget(self.txn_table)

        self.txn_btn_layout = QHBoxLayout()
        self.txn_btn_layout.setObjectName(u"txn_btn_layout")
        self.btn_add_txn = QPushButton(self.tab_txn)
        self.btn_add_txn.setObjectName(u"btn_add_txn")

        self.txn_btn_layout.addWidget(self.btn_add_txn)

        self.btn_import_csv = QPushButton(self.tab_txn)
        self.btn_import_csv.setObjectName(u"btn_import_csv")

        self.txn_btn_layout.addWidget(self.btn_import_csv)

        self.btn_delete_txn = QPushButton(self.tab_txn)
        self.btn_delete_txn.setObjectName(u"btn_delete_txn")

        self.txn_btn_layout.addWidget(self.btn_delete_txn)

        self.txn_btn_spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.txn_btn_layout.addItem(self.txn_btn_spacer)


        self.txn_tab_layout.addLayout(self.txn_btn_layout)

        self.tabs.addTab(self.tab_txn, "")
        self.tab_budget = QWidget()
        self.tab_budget.setObjectName(u"tab_budget")
        self.budget_tab_layout = QVBoxLayout(self.tab_budget)
        self.budget_tab_layout.setObjectName(u"budget_tab_layout")
        self.budget_table = QTableWidget(self.tab_budget)
        if (self.budget_table.columnCount() < 5):
            self.budget_table.setColumnCount(5)
        __qtablewidgetitem6 = QTableWidgetItem()
        self.budget_table.setHorizontalHeaderItem(0, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        self.budget_table.setHorizontalHeaderItem(1, __qtablewidgetitem7)
        __qtablewidgetitem8 = QTableWidgetItem()
        self.budget_table.setHorizontalHeaderItem(2, __qtablewidgetitem8)
        __qtablewidgetitem9 = QTableWidgetItem()
        self.budget_table.setHorizontalHeaderItem(3, __qtablewidgetitem9)
        __qtablewidgetitem10 = QTableWidgetItem()
        self.budget_table.setHorizontalHeaderItem(4, __qtablewidgetitem10)
        self.budget_table.setObjectName(u"budget_table")
        self.budget_table.setAlternatingRowColors(True)
        self.budget_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.budget_table.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.budget_table.horizontalHeader().setStretchLastSection(True)

        self.budget_tab_layout.addWidget(self.budget_table)

        self.budget_btn_layout = QHBoxLayout()
        self.budget_btn_layout.setObjectName(u"budget_btn_layout")
        self.btn_add_budget = QPushButton(self.tab_budget)
        self.btn_add_budget.setObjectName(u"btn_add_budget")

        self.budget_btn_layout.addWidget(self.btn_add_budget)

        self.btn_delete_budget = QPushButton(self.tab_budget)
        self.btn_delete_budget.setObjectName(u"btn_delete_budget")

        self.budget_btn_layout.addWidget(self.btn_delete_budget)

        self.budget_btn_spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.budget_btn_layout.addItem(self.budget_btn_spacer)


        self.budget_tab_layout.addLayout(self.budget_btn_layout)

        self.budget_summary_label = QLabel(self.tab_budget)
        self.budget_summary_label.setObjectName(u"budget_summary_label")
        self.budget_summary_label.setStyleSheet(u"font-weight: bold; padding: 4px; color: #333;")

        self.budget_tab_layout.addWidget(self.budget_summary_label)

        self.budget_rule_group = QGroupBox(self.tab_budget)
        self.budget_rule_group.setObjectName(u"budget_rule_group")
        self.budget_rule_layout = QHBoxLayout(self.budget_rule_group)
        self.budget_rule_layout.setObjectName(u"budget_rule_layout")
        self.income_label = QLabel(self.budget_rule_group)
        self.income_label.setObjectName(u"income_label")

        self.budget_rule_layout.addWidget(self.income_label)

        self.income_edit = QLineEdit(self.budget_rule_group)
        self.income_edit.setObjectName(u"income_edit")
        self.income_edit.setMaximumSize(QSize(80, 16777215))

        self.budget_rule_layout.addWidget(self.income_edit)

        self.rule_label = QLabel(self.budget_rule_group)
        self.rule_label.setObjectName(u"rule_label")

        self.budget_rule_layout.addWidget(self.rule_label)

        self.radio_503020 = QRadioButton(self.budget_rule_group)
        self.radio_503020.setObjectName(u"radio_503020")
        self.radio_503020.setChecked(True)

        self.budget_rule_layout.addWidget(self.radio_503020)

        self.radio_fixed = QRadioButton(self.budget_rule_group)
        self.radio_fixed.setObjectName(u"radio_fixed")

        self.budget_rule_layout.addWidget(self.radio_fixed)

        self.btn_apply_503020 = QPushButton(self.budget_rule_group)
        self.btn_apply_503020.setObjectName(u"btn_apply_503020")

        self.budget_rule_layout.addWidget(self.btn_apply_503020)

        self.btn_apply_fixed = QPushButton(self.budget_rule_group)
        self.btn_apply_fixed.setObjectName(u"btn_apply_fixed")

        self.budget_rule_layout.addWidget(self.btn_apply_fixed)

        self.budget_rule_spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.budget_rule_layout.addItem(self.budget_rule_spacer)


        self.budget_tab_layout.addWidget(self.budget_rule_group)

        self.tabs.addTab(self.tab_budget, "")
        self.tab_diag = QWidget()
        self.tab_diag.setObjectName(u"tab_diag")
        self.diag_tab_layout = QVBoxLayout(self.tab_diag)
        self.diag_tab_layout.setObjectName(u"diag_tab_layout")
        self.diag_text = QTextEdit(self.tab_diag)
        self.diag_text.setObjectName(u"diag_text")
        self.diag_text.setReadOnly(True)
        font = QFont()
        font.setFamilies([u"Microsoft YaHei"])
        font.setPointSize(10)
        self.diag_text.setFont(font)

        self.diag_tab_layout.addWidget(self.diag_text)

        self.diag_btn_layout = QHBoxLayout()
        self.diag_btn_layout.setObjectName(u"diag_btn_layout")
        self.btn_run_diag = QPushButton(self.tab_diag)
        self.btn_run_diag.setObjectName(u"btn_run_diag")

        self.diag_btn_layout.addWidget(self.btn_run_diag)

        self.diag_btn_spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.diag_btn_layout.addItem(self.diag_btn_spacer)


        self.diag_tab_layout.addLayout(self.diag_btn_layout)

        self.tabs.addTab(self.tab_diag, "")
        self.tab_savings = QWidget()
        self.tab_savings.setObjectName(u"tab_savings")
        self.savings_tab_layout = QVBoxLayout(self.tab_savings)
        self.savings_tab_layout.setObjectName(u"savings_tab_layout")
        self.savings_goal_group = QGroupBox(self.tab_savings)
        self.savings_goal_group.setObjectName(u"savings_goal_group")
        self.goal_group_layout = QVBoxLayout(self.savings_goal_group)
        self.goal_group_layout.setObjectName(u"goal_group_layout")
        self.goal_input_layout = QHBoxLayout()
        self.goal_input_layout.setObjectName(u"goal_input_layout")
        self.target_label = QLabel(self.savings_goal_group)
        self.target_label.setObjectName(u"target_label")

        self.goal_input_layout.addWidget(self.target_label)

        self.target_edit = QLineEdit(self.savings_goal_group)
        self.target_edit.setObjectName(u"target_edit")
        self.target_edit.setMaximumSize(QSize(80, 16777215))

        self.goal_input_layout.addWidget(self.target_edit)

        self.months_label = QLabel(self.savings_goal_group)
        self.months_label.setObjectName(u"months_label")

        self.goal_input_layout.addWidget(self.months_label)

        self.months_edit = QLineEdit(self.savings_goal_group)
        self.months_edit.setObjectName(u"months_edit")
        self.months_edit.setMaximumSize(QSize(60, 16777215))

        self.goal_input_layout.addWidget(self.months_edit)

        self.btn_run_goal = QPushButton(self.savings_goal_group)
        self.btn_run_goal.setObjectName(u"btn_run_goal")

        self.goal_input_layout.addWidget(self.btn_run_goal)

        self.goal_input_spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.goal_input_layout.addItem(self.goal_input_spacer)


        self.goal_group_layout.addLayout(self.goal_input_layout)

        self.goal_text = QTextEdit(self.savings_goal_group)
        self.goal_text.setObjectName(u"goal_text")
        self.goal_text.setReadOnly(True)
        self.goal_text.setFont(font)
        self.goal_text.setMaximumSize(QSize(16777215, 220))

        self.goal_group_layout.addWidget(self.goal_text)


        self.savings_tab_layout.addWidget(self.savings_goal_group)

        self.savings_method_group = QGroupBox(self.tab_savings)
        self.savings_method_group.setObjectName(u"savings_method_group")
        self.method_group_layout = QVBoxLayout(self.savings_method_group)
        self.method_group_layout.setObjectName(u"method_group_layout")
        self.method_input_layout = QHBoxLayout()
        self.method_input_layout.setObjectName(u"method_input_layout")
        self.method_label = QLabel(self.savings_method_group)
        self.method_label.setObjectName(u"method_label")

        self.method_input_layout.addWidget(self.method_label)

        self.radio_fixed_amount = QRadioButton(self.savings_method_group)
        self.radio_fixed_amount.setObjectName(u"radio_fixed_amount")
        self.radio_fixed_amount.setChecked(True)

        self.method_input_layout.addWidget(self.radio_fixed_amount)

        self.radio_52w_inc = QRadioButton(self.savings_method_group)
        self.radio_52w_inc.setObjectName(u"radio_52w_inc")

        self.method_input_layout.addWidget(self.radio_52w_inc)

        self.radio_52w_dec = QRadioButton(self.savings_method_group)
        self.radio_52w_dec.setObjectName(u"radio_52w_dec")

        self.method_input_layout.addWidget(self.radio_52w_dec)

        self.radio_pct = QRadioButton(self.savings_method_group)
        self.radio_pct.setObjectName(u"radio_pct")

        self.method_input_layout.addWidget(self.radio_pct)

        self.method_param_label = QLabel(self.savings_method_group)
        self.method_param_label.setObjectName(u"method_param_label")

        self.method_input_layout.addWidget(self.method_param_label)

        self.method_param_edit = QLineEdit(self.savings_method_group)
        self.method_param_edit.setObjectName(u"method_param_edit")
        self.method_param_edit.setMaximumSize(QSize(60, 16777215))

        self.method_input_layout.addWidget(self.method_param_edit)

        self.saving_income_label = QLabel(self.savings_method_group)
        self.saving_income_label.setObjectName(u"saving_income_label")

        self.method_input_layout.addWidget(self.saving_income_label)

        self.saving_income_edit = QLineEdit(self.savings_method_group)
        self.saving_income_edit.setObjectName(u"saving_income_edit")
        self.saving_income_edit.setMaximumSize(QSize(80, 16777215))

        self.method_input_layout.addWidget(self.saving_income_edit)

        self.btn_run_method = QPushButton(self.savings_method_group)
        self.btn_run_method.setObjectName(u"btn_run_method")

        self.method_input_layout.addWidget(self.btn_run_method)

        self.method_input_spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.method_input_layout.addItem(self.method_input_spacer)


        self.method_group_layout.addLayout(self.method_input_layout)

        self.method_desc_label = QLabel(self.savings_method_group)
        self.method_desc_label.setObjectName(u"method_desc_label")
        self.method_desc_label.setStyleSheet(u"color: #555; font-size: 12px; padding: 2px 8px; background: #f5f5f5; border-radius: 3px;")
        self.method_desc_label.setWordWrap(True)

        self.method_group_layout.addWidget(self.method_desc_label)

        self.method_text = QTextEdit(self.savings_method_group)
        self.method_text.setObjectName(u"method_text")
        self.method_text.setReadOnly(True)
        self.method_text.setFont(font)

        self.method_group_layout.addWidget(self.method_text)


        self.savings_tab_layout.addWidget(self.savings_method_group)

        self.tabs.addTab(self.tab_savings, "")
        self.tab_alert = QWidget()
        self.tab_alert.setObjectName(u"tab_alert")
        self.alert_tab_layout = QVBoxLayout(self.tab_alert)
        self.alert_tab_layout.setObjectName(u"alert_tab_layout")
        self.alert_text = QTextEdit(self.tab_alert)
        self.alert_text.setObjectName(u"alert_text")
        self.alert_text.setReadOnly(True)
        self.alert_text.setFont(font)

        self.alert_tab_layout.addWidget(self.alert_text)

        self.alert_btn_layout = QHBoxLayout()
        self.alert_btn_layout.setObjectName(u"alert_btn_layout")
        self.btn_refresh_alert = QPushButton(self.tab_alert)
        self.btn_refresh_alert.setObjectName(u"btn_refresh_alert")

        self.alert_btn_layout.addWidget(self.btn_refresh_alert)

        self.btn_check_alert = QPushButton(self.tab_alert)
        self.btn_check_alert.setObjectName(u"btn_check_alert")

        self.alert_btn_layout.addWidget(self.btn_check_alert)

        self.btn_clear_alert = QPushButton(self.tab_alert)
        self.btn_clear_alert.setObjectName(u"btn_clear_alert")

        self.alert_btn_layout.addWidget(self.btn_clear_alert)

        self.alert_btn_spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.alert_btn_layout.addItem(self.alert_btn_spacer)


        self.alert_tab_layout.addLayout(self.alert_btn_layout)

        self.tabs.addTab(self.tab_alert, "")

        self.central_layout.addWidget(self.tabs)

        MainWindow.setCentralWidget(self.centralwidget)
        self.toolbar_month = QToolBar(MainWindow)
        self.toolbar_month.setObjectName(u"toolbar_month")
        self.toolbar_month.setMovable(False)
        MainWindow.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar_month)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.tabs.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"\u4e2a\u4eba\u8d22\u52a1\u7ba1\u7406\u7cfb\u7edf", None))
        ___qtablewidgetitem = self.txn_table.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MainWindow", u"\u65e5\u671f", None))
        ___qtablewidgetitem1 = self.txn_table.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MainWindow", u"\u7c7b\u578b", None))
        ___qtablewidgetitem2 = self.txn_table.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("MainWindow", u"\u7c7b\u522b", None))
        ___qtablewidgetitem3 = self.txn_table.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("MainWindow", u"\u91d1\u989d", None))
        ___qtablewidgetitem4 = self.txn_table.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("MainWindow", u"\u8d26\u6237", None))
        ___qtablewidgetitem5 = self.txn_table.horizontalHeaderItem(5)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("MainWindow", u"\u5907\u6ce8", None))
        self.btn_add_txn.setText(QCoreApplication.translate("MainWindow", u"\u6dfb\u52a0\u4ea4\u6613", None))
        self.btn_import_csv.setText(QCoreApplication.translate("MainWindow", u"\u5bfc\u5165CSV", None))
        self.btn_delete_txn.setText(QCoreApplication.translate("MainWindow", u"\u5220\u9664\u9009\u4e2d", None))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_txn), QCoreApplication.translate("MainWindow", u"\u4ea4\u6613\u7ba1\u7406", None))
        ___qtablewidgetitem6 = self.budget_table.horizontalHeaderItem(0)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("MainWindow", u"\u7c7b\u522b", None))
        ___qtablewidgetitem7 = self.budget_table.horizontalHeaderItem(1)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("MainWindow", u"\u6708\u5ea6\u9650\u989d", None))
        ___qtablewidgetitem8 = self.budget_table.horizontalHeaderItem(2)
        ___qtablewidgetitem8.setText(QCoreApplication.translate("MainWindow", u"\u5df2\u652f\u51fa", None))
        ___qtablewidgetitem9 = self.budget_table.horizontalHeaderItem(3)
        ___qtablewidgetitem9.setText(QCoreApplication.translate("MainWindow", u"\u5269\u4f59", None))
        ___qtablewidgetitem10 = self.budget_table.horizontalHeaderItem(4)
        ___qtablewidgetitem10.setText(QCoreApplication.translate("MainWindow", u"\u72b6\u6001", None))
        self.btn_add_budget.setText(QCoreApplication.translate("MainWindow", u"\u6dfb\u52a0\u9884\u7b97\u7c7b\u522b", None))
        self.btn_delete_budget.setText(QCoreApplication.translate("MainWindow", u"\u5220\u9664\u9009\u4e2d\u9884\u7b97", None))
        self.budget_summary_label.setText("")
        self.budget_rule_group.setTitle(QCoreApplication.translate("MainWindow", u"\u9884\u7b97\u89c4\u5219", None))
        self.income_label.setText(QCoreApplication.translate("MainWindow", u"\u6708\u6536\u5165:", None))
        self.income_edit.setText(QCoreApplication.translate("MainWindow", u"5000", None))
        self.rule_label.setText(QCoreApplication.translate("MainWindow", u"  \u89c4\u5219:", None))
        self.radio_503020.setText(QCoreApplication.translate("MainWindow", u"50/30/20", None))
        self.radio_fixed.setText(QCoreApplication.translate("MainWindow", u"\u56fa\u5b9a\u9884\u7b97", None))
        self.btn_apply_503020.setText(QCoreApplication.translate("MainWindow", u"\u8bbe\u7f6e\u9884\u7b97", None))
#if QT_CONFIG(tooltip)
        self.btn_apply_503020.setToolTip(QCoreApplication.translate("MainWindow", u"\u6309 50/30/20 \u89c4\u5219\uff0c\u6839\u636e\u6708\u6536\u5165\u81ea\u52a8\u5206\u914d\u5404\u7c7b\u522b\u9884\u7b97", None))
#endif // QT_CONFIG(tooltip)
        self.btn_apply_fixed.setText(QCoreApplication.translate("MainWindow", u"\u91c7\u7528\u56fa\u5b9a\u9884\u7b97", None))
#if QT_CONFIG(tooltip)
        self.btn_apply_fixed.setToolTip(QCoreApplication.translate("MainWindow", u"\u4f7f\u7528\u9884\u8bbe\u56fa\u5b9a\u91d1\u989d\u9884\u7b97\uff08\u4e0d\u4f9d\u8d56\u6708\u6536\u5165\uff09", None))
#endif // QT_CONFIG(tooltip)
        self.tabs.setTabText(self.tabs.indexOf(self.tab_budget), QCoreApplication.translate("MainWindow", u"\u9884\u7b97\u7ba1\u7406", None))
        self.btn_run_diag.setText(QCoreApplication.translate("MainWindow", u"\u751f\u6210\u8bca\u65ad\u62a5\u544a", None))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_diag), QCoreApplication.translate("MainWindow", u"\u8bca\u65ad\u62a5\u544a", None))
        self.savings_goal_group.setTitle(QCoreApplication.translate("MainWindow", u"\u50a8\u84c4\u76ee\u6807\u5012\u63a8", None))
        self.target_label.setText(QCoreApplication.translate("MainWindow", u"\u76ee\u6807\u91d1\u989d:", None))
        self.target_edit.setText(QCoreApplication.translate("MainWindow", u"12000", None))
        self.months_label.setText(QCoreApplication.translate("MainWindow", u"  \u6708\u6570:", None))
        self.months_edit.setText(QCoreApplication.translate("MainWindow", u"12", None))
        self.btn_run_goal.setText(QCoreApplication.translate("MainWindow", u"\u8ba1\u7b97\u5012\u63a8\u8ba1\u5212", None))
        self.savings_method_group.setTitle(QCoreApplication.translate("MainWindow", u"\u50a8\u84c4\u65b9\u6cd5\u9009\u62e9", None))
        self.method_label.setText(QCoreApplication.translate("MainWindow", u"\u50a8\u84c4\u65b9\u6cd5:", None))
        self.radio_fixed_amount.setText(QCoreApplication.translate("MainWindow", u"\u56fa\u5b9a\u91d1\u989d", None))
        self.radio_52w_inc.setText(QCoreApplication.translate("MainWindow", u"52\u5468\u9012\u589e", None))
        self.radio_52w_dec.setText(QCoreApplication.translate("MainWindow", u"52\u5468\u9012\u51cf", None))
        self.radio_pct.setText(QCoreApplication.translate("MainWindow", u"\u6536\u5165%", None))
        self.method_param_label.setText(QCoreApplication.translate("MainWindow", u"  \u53c2\u6570:", None))
        self.method_param_edit.setText(QCoreApplication.translate("MainWindow", u"500", None))
        self.saving_income_label.setText(QCoreApplication.translate("MainWindow", u"  \u6708\u6536\u5165:", None))
        self.saving_income_edit.setText(QCoreApplication.translate("MainWindow", u"5000", None))
        self.btn_run_method.setText(QCoreApplication.translate("MainWindow", u"\u8ba1\u7b97\u50a8\u84c4\u8ba1\u5212", None))
        self.method_desc_label.setText("")
        self.tabs.setTabText(self.tabs.indexOf(self.tab_savings), QCoreApplication.translate("MainWindow", u"\u50a8\u84c4\u7ba1\u7406", None))
        self.btn_refresh_alert.setText(QCoreApplication.translate("MainWindow", u"\u5237\u65b0", None))
        self.btn_check_alert.setText(QCoreApplication.translate("MainWindow", u"\u68c0\u6d4b\u9884\u8b66", None))
        self.btn_clear_alert.setText(QCoreApplication.translate("MainWindow", u"\u6e05\u7a7a\u9884\u8b66", None))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_alert), QCoreApplication.translate("MainWindow", u"\u9884\u8b66\u6d88\u606f", None))
        self.toolbar_month.setWindowTitle(QCoreApplication.translate("MainWindow", u"\u6708\u4efd", None))
    # retranslateUi

