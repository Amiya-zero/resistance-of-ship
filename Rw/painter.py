#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: Gotthard   time: 2020/12/18
# 快捷键 ctrl+D 复制一行 ctrl+Y 删除一行 Shift+TAB 删除缩进
# TAB 缩进  Shift+Enter 换行
# Ctrl+F 搜索 Ctrl+Shift+'-' 全部折叠 Ctrl+A 全选
from mainwindow import Ui_MainWindow
from calculator import Calculator
import setting
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator
import numpy as np
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
matplotlib.use('Qt5Agg')


class MyFigure(FigureCanvas):
    def __init__(self, width=5, height=4, dpi=100):
        self.figure = Figure(figsize=(width, height), dpi=dpi)
        super(MyFigure, self).__init__(self.figure)

class Ui_Main(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(Ui_Main, self).__init__()
        self.setupUi(self)
        self.setWindowTitle('ship resistance')
        self.F = MyFigure()
        self.calculator = Calculator()
        self.grid = QGridLayout(self.groupBox)
        self.grid.addWidget(self.F, 0, 1)

        # 设置校验器，限制输入
        doublereg = QRegExp('[0-9]+.[0-9]+$')
        doublevalidator = QRegExpValidator(self)
        doublevalidator.setRegExp(doublereg)
        intreg = QRegExp('[0-9]+$')
        intvalidator = QRegExpValidator(self)
        intvalidator.setRegExp(intreg)
        self.lineEdit.setValidator(doublevalidator)
        self.lineEdit_2.setValidator(doublevalidator)
        self.lineEdit_3.setValidator(intvalidator)
        self.lineEdit_4.setValidator(doublevalidator)
        self.lineEdit_5.setValidator(doublevalidator)
        self.lineEdit_6.setValidator(doublevalidator)

        # 绑定事件
        self.pushButton.clicked.connect(self.change_parameters)
        self.pushButton_2.clicked.connect(self.draw_ship)
        self.pushButton_3.clicked.connect(self.draw_Cw)
        self.pushButton_4.clicked.connect(self.write_to_file)
        self.pushButton_5.clicked.connect(self.quit)

    # 设置参数
    def change_parameters(self):
        v1 = self.lineEdit.text()
        v2 = self.lineEdit_2.text()
        v3 = self.lineEdit_3.text()
        v4 = self.lineEdit_4.text()
        v5 = self.lineEdit_5.text()
        v6 = self.lineEdit_6.text()
        # 设置提醒弹窗
        if not len(v1):
            QMessageBox.information(self, '提醒', '请输入最大傅汝德数Frmax', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            return
        if not len(v2):
            QMessageBox.information(self, '提醒', '请输入最小傅汝德数Frmin', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            return
        if not len(v3):
            QMessageBox.information(self, '提醒', '请输入区间数n', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            return
        if not len(v4):
            QMessageBox.information(self, '提醒', '请输入船长Lpp', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            return
        if not len(v5):
            QMessageBox.information(self, '提醒', '请输入型宽B', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            return
        if not len(v6):
            QMessageBox.information(self, '提醒', '请输入型深D', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            return
        else:
            self.calculator.Frmin = float(v1)
            self.calculator.Frmax = float(v2)
            self.calculator.n = int(v3)
            self.calculator.Lpp = float(v4)
            self.calculator.B = float(v5)
            self.calculator.D = float(v6)
            self.statusbar.showMessage('设置完毕', 3000)

    # 绘制船型
    def draw_ship(self):
        x = np.linspace(-self.calculator.Lpp / 2, self.calculator.Lpp / 2, 1000)
        z = np.linspace(0, self.calculator.D, 1000)
        X, Z = np.meshgrid(x, z)
        y = self.calculator.get_f(X, Z)
        Y = y.T
        self.F.figure.clear()
        axes = self.F.figure.add_subplot(111, projection='3d')
        axes.plot_surface(X, Y, Z, rstride=1, cstride=1, linewidth=0, cmap='rainbow')
        axes.plot_surface(X, -Y, Z, rstride=1, cstride=1, linewidth=0, cmap='rainbow')
        self.F.figure.canvas.draw()
        self.statusbar.showMessage('绘制完成', 3000)

    # 绘制曲线
    def draw_Cw(self):
        self.calculator.main()
        self.F.figure.clear()
        axes = self.F.figure.add_subplot(111)
        axes.plot(setting.data['Fr'], setting.data['Cw'])
        self.F.figure.canvas.draw()
        str1 = '计算计算完成，共用' + str(int(setting.time)+1) + '秒'
        self.statusbar.showMessage(str1, 3000)

    # 将Cw写入文件
    def write_to_file(self):
        setting.data.to_excel('Cw.xlsx')
        self.statusbar.showMessage('数据保存完成', 3000)

    # 退出程序
    def quit(self):
        QMessageBox.question(self, '警告', '您正在退出程序，是否确认退出', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        app = QApplication.instance()
        # 退出应用程序
        app.quit()