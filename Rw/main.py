#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: Amiya   time: 2020/12/8
# 快捷键 ctrl+D 复制一行 ctrl+Y 删除一行 Shift+TAB 删除缩进
# TAB 缩进  Shift+Enter 换行
# Ctrl+F 搜索 Ctrl+Shift+'-' 全部折叠 Ctrl+A 全选
from painter import Ui_Main
import sys
import multiprocessing
from PyQt5.QtWidgets import QApplication


if __name__ == '__main__':
    multiprocessing.freeze_support()
    app = QApplication(sys.argv)
    main = Ui_Main()
    main.show()
    sys.exit(app.exec_())
