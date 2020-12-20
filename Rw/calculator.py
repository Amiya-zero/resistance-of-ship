#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: Gotthard   time: 2020/12/8
# 快捷键 ctrl+D 复制一行 ctrl+Y 删除一行 Shift+TAB 删除缩进
# TAB 缩进  Shift+Enter 换行
# Ctrl+F 搜索 Ctrl+Shift+'-' 全部折叠 Ctrl+A 全选
import numpy as np
from scipy.integrate import dblquad
import setting
from multiprocessing import Process, Manager
import multiprocessing
import pandas as pd
import time


class Calculator:
    def __init__(self):
        self.Frmax = 1
        self.Frmin = 0.1
        self.n = 300
        self.Lpp = 3
        self.B = 0.3
        self.D = 0.1875

    def get_Fr(self):
        Fr = np.linspace(self.Frmin, self.Frmax, self.n)
        return Fr

    def get_v(self):
        v = np.sqrt(setting.g * self.Lpp) * self.get_Fr()
        return v

    # 函数f表达式
    def get_f(self, x, z):
        f = 2 * self.B * (0.25 - (x / self.Lpp) ** 2) * (1 - (z / self.D) ** 2)
        return f

    # 计算f对x的偏导fx
    def get_grad_x(self, x, z):
        fx = -4 * self.B * (x / self.Lpp ** 2) * (1 - (z / self.D) ** 2)
        return fx

    # 计算f对z的偏导fz
    def get_grad_z(self, x, z):
        fz = -4 * self.B * (1 / 4 - (x / self.Lpp) ** 2) * (z / self.D ** 2)
        return fz

    # 计算湿表面积s
    def get_S(self):
        S, error = dblquad(lambda z, x: np.sqrt(self.get_grad_x(x, z) ** 2 + self.get_grad_z(x, z) ** 2 + 1), -self.Lpp / 2, self.Lpp / 2, 0, self.D)
        return S

    # 得到被积函数
    def get_i_j(self, x, z, angle, u):
        K0 = setting.g / u ** 2
        i = self.get_grad_x(x, z) * np.exp(K0 * z / (np.cos(angle) ** 2)) * np.cos(K0 * x / np.cos(angle))
        j = self.get_grad_x(x, z) * np.exp(K0 * z / (np.cos(angle) ** 2)) * np.sin(K0 * x / np.cos(angle))
        return i, j

    # 得到I+iJ 返回被积函数f
    def get_I_J(self, angle, u):
        I, error_1 = dblquad(lambda z, x: self.get_i_j(x, z, angle, u)[0], -self.Lpp / 2, self.Lpp / 2, -self.D, 0)
        J, error_2 = dblquad(lambda z, x: self.get_i_j(x, z, angle, u)[1], -self.Lpp / 2, self.Lpp / 2, -self.D, 0)
        f = (I ** 2 + J ** 2) / (np.cos(angle) ** 3)
        return f

    # 求Rw,复化梯形公式
    def get_Rw(self, u):
        K0 = setting.g / u ** 2
        # 定义步长
        n = 40
        h = np.pi / 2 / n
        result = 0
        for i in range(0, n):
            angle_0 = h * i
            angle_1 = h * (i + 1)
            result += (self.get_I_J(angle_0, u) + self.get_I_J(angle_1, u)) / 2 * h
        Rw = 4 * setting.p * setting.g * K0 / np.pi * result
        Cw = Rw / (1 / 2 * setting.p * u ** 2 * self.get_S())
        return Cw

    # 利用多线程处理数据
    def process(self, list_, v, position):
        for i in range(0, int(self.n / 4)):
            self.process_data(list_, v, position, i)

    # 数据处理
    def process_data(self, list_, v, position, i):
        cw = self.get_Rw(v[position * int(self.n / 4) + i])
        while len(list_) != i:
            continue
        list_.append(cw)

    # 开启多线程,主函数
    def main(self):
        Fr = self.get_Fr()
        v = self.get_v()
        start = time.time()
        Cw1 = Manager().list()
        Cw2 = Manager().list()
        Cw3 = Manager().list()
        Cw4 = Manager().list()
        Cww = [Cw1, Cw2, Cw3, Cw4]
        Cw = list()
        for i in range(0, 4):
            p = Process(target=self.process, args=(Cww[i], v, i))
            p.start()
            p.join()
        while len(Cw1) != int(self.n / 4):
            continue
        while len(Cw2) != int(self.n / 4):
            continue
        while len(Cw3) != int(self.n / 4):
            continue
        while len(Cw4) != int(self.n / 4):
            continue
        Cw.extend(Cw1)
        Cw.extend(Cw2)
        Cw.extend(Cw3)
        Cw.extend(Cw4)
        end = time.time()
        setting.data = pd.DataFrame({'Fr': Fr, 'Cw': Cw})
        setting.time = end - start


if __name__ == '__main__':
    multiprocessing.freeze_support()
    calculator = Calculator()
    calculator.main()
    print(setting.time, setting.data)
