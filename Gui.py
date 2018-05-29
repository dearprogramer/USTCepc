# coding=utf-8
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
import platform
import sys
import common
import time
from pandas import *


class loginDisplay(QDialog):
    def __init__(self, picurl, parent=None):
        super(loginDisplay, self).__init__(parent)
        self.datadic = dict()
        # self.picurl=picurl
        self.lable_id = QLabel("学号")
        self.line_id = QLineEdit()
        self.lable_password = QLabel("密码：")
        self.line_password = QLineEdit()
        self.lable_id.setBuddy(self.line_id)
        self.lable_checknum = QLabel("验证码：")
        self.login = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.lable_id.setBuddy(self.line_id)
        self.lable_password.setBuddy(self.line_password)
        self.grid = QGridLayout()
        self.line_checknum = QLineEdit()
        self.grid.addWidget(self.lable_id, 0, 0, 1, 1)
        self.grid.addWidget(self.line_id, 0, 1, 1, 2)
        self.grid.addWidget(self.lable_password, 1, 0, 1, 1)
        self.grid.addWidget(self.line_password, 1, 1, 1, 2)
        self.grid.addWidget(self.lable_checknum, 2, 0, 1, 1)
        self.lable_pic = QLabel()
        self.lable_pic.setFixedSize(40, 10)
        self.pic = QPixmap(picurl)
        self.lable_pic.setPixmap(self.pic)
        self.grid.addWidget(self.lable_pic, 2, 1, 1, 1)
        self.grid.addWidget(self.line_checknum, 2, 2, 1, 1)
        self.grid.addWidget(self.login, 3, 0, 1, 3)
        self.setLayout(self.grid)
        self.login.accepted.connect(self.dataaccept)
        self.show()

    def checkFormat(self):
        if self.studentid != "" and self.password != "" and len(self.checknum) == 4:
            return 1
        else:
            return 0

    def dataaccept(self):
        self.studentid = self.line_id.text().strip()
        self.password = self.line_password.text().strip()
        self.checknum = self.line_checknum.text().strip()
        if self.checkFormat():
            self.datadic.__setitem__("id", self.studentid)
            self.datadic.__setitem__("password", self.password)
            self.datadic.__setitem__("checknum", self.checknum)
            self.accept()
        else:
            QMessageBox.about(self, '警告!', '信息不完整!')


class BPButton(QPushButton):
    newclicked = pyqtSignal([str, int])

    def __init__(self, name, id, text=None, parent=None):
        super(BPButton, self).__init__(text, parent=parent)
        self.id = id
        self.name = name
        self.clicked.connect(self.emitNewInfo)

    def emitNewInfo(self):
        self.newclicked[str, int].emit(self.name, self.id)


class MainWin(QMainWindow):
    def __init__(self, parent=None):
        super(MainWin, self).__init__(parent)
        self.initialMainframe()
        self.reserve_select_dict = dict()
        self.infp = common.ImfoProcess()
        self.reseveState = 0
        self.islogin = 0
        self.booksize = 0
        self.qtime = QTimer(self)
        self.qtime.timeout.connect(self.updateCourseInfo)
        self.bookchangelist = {1: list(), 2: list()}
        self.availuableReserve = 0
        self.availuableChange = 0

    def initialMainframe(self):
        self.image = QImage()
        self.dirty = False
        self.filename = None
        self.mirroredvertically = False
        self.mirroredhorizontally = False
        self.reserveinfoitems = 0
        self.menu = QMenuBar()
        self.accout = self.menu.addMenu("用户")
        self.reservation = self.menu.addAction("预约信息")
        self.course = self.menu.addAction("课程查询")
        self.classReserve = self.menu.addAction("预约课程")
        self.logaction = self.accout.addAction("登录")
        self.logoutaction = self.accout.addAction("注销")
        self.logaction.triggered.connect(self.login)
        self.logoutaction.triggered.connect(self.logout)
        self.classReserve.triggered.connect(self.displayReserve)
        self.reservation.triggered.connect(self.displaybook)
        self.course.triggered.connect(self.displayCourse)
        # self.accout.addAction(self.logaction)
        # self.accout.addAction(self.logoutaction)
        self.setMenuBar(self.menu)
        self.setMinimumSize(900, 300)
        self.lable_info = QLabel("我爱你")
        self.lable_course = QLabel("I miss you !")
        palette1 = QPalette()
        palette1.setColor(self.backgroundRole(), QColor(0, 253, 123))
        self.setPalette(palette1)
        self.stack_center = QStackedWidget()
        self.table_course = QTableWidget(10, 13)
        self.table_course.setHorizontalHeaderLabels(["课题", "周数", "星期", "老师", "课时", "上课时间", "地点", "开始预定时间", "结束预定时间",
                                                     "可预约", "已预约", "预定", "状态"])
        self.stack_center.addWidget(self.lable_info)
        self.stack_center.addWidget(self.lable_course)
        self.stack_center.addWidget(self.table_course)
        self.initReservePage()
        self.stack_center.addWidget(self.frame_course)
        self.initBookinfo()
        self.stack_center.addWidget(self.frame_book)
        self.setCentralWidget(self.stack_center)
        self.status = self.statusBar()

    def initReservePage(self):
        self.box_course = QComboBox()
        self.box_course.addItem("Situational Dialogue", 2001)
        self.box_course.addItem("Topical Discussion", 2002)
        self.box_course.addItem("Debate", 2003)
        self.box_course.addItem("Drama", 2004)
        self.box_day = QComboBox()
        self.box_day.addItem("不限", 0)
        self.box_day.addItem("一", 1)
        self.box_day.addItem("二", 2)
        self.box_day.addItem("三", 3)
        self.box_day.addItem("四", 4)
        self.box_day.addItem("五", 5)
        self.box_day.addItem("六", 6)
        self.box_day.addItem("日", 7)
        self.box_coursetime = QComboBox()
        self.cousetime1 = {"08:25": 1, "16:40": 4}
        self.cousetime2 = {"09:45": 2, "14:30": 3, "19:00": 5}
        self.box_time_change()
        self.box_course.currentIndexChanged.connect(self.box_time_change)
        self.box_week = QComboBox()
        self.box_week.addItem("最近周", 0)
        for i in range(19):
            self.box_week.addItem("第" + str(i + 1) + "周", i + 1)
        self.blayout_course = QVBoxLayout()
        self.blayout_courseTitle = QHBoxLayout()
        self.lable_course_name = QLabel("课程类型:")
        self.lable_course_time = QLabel("时间：")
        self.lable_course_week = QLabel("周数")
        self.lable_course_day = QLabel("星期")
        self.button_checked = QPushButton("选定")
        self.blayout_courseTitle.addWidget(self.lable_course_name)
        self.blayout_courseTitle.addWidget(self.box_course)
        self.blayout_courseTitle.addWidget(self.lable_course_time)
        self.blayout_courseTitle.addWidget(self.box_coursetime)
        self.blayout_courseTitle.addWidget(self.lable_course_day)
        self.blayout_courseTitle.addWidget(self.box_day)
        self.blayout_courseTitle.addWidget(self.lable_course_week)
        self.blayout_courseTitle.addWidget(self.box_week)
        self.blayout_courseTitle.addWidget(self.button_checked)
        self.blayout_course.addLayout(self.blayout_courseTitle)
        self.table_coursedisplay = QTableWidget(5, 5)
        self.table_coursedisplay.setHorizontalHeaderLabels(["课程类型", "时间", "周数", "星期", "操作"])
        self.blayout_course.addWidget(self.table_coursedisplay)
        self.button_checked.clicked.connect(self.addReserve)
        self.frame_course = QFrame()
        self.blayout_courseMiddle = QHBoxLayout()
        self.bg_course = QButtonGroup()
        self.button_courseClear = QPushButton("清除")
        self.button_courseExcute = QPushButton("执行")
        self.bg_course.addButton(self.button_courseExcute)
        self.bg_course.addButton(self.button_courseClear)
        self.blayout_courseMiddle.addWidget(self.button_courseExcute)
        self.blayout_courseMiddle.addWidget(self.button_courseClear)
        # self.blayout_course.addWidget(self.bg_course)
        self.blayout_courseMiddle.addStretch(5)
        self.blayout_course.addLayout(self.blayout_courseMiddle)
        self.frame_course.setLayout(self.blayout_course)
        self.button_courseExcute.clicked.connect(self.reserveExcute)
        self.button_courseClear.clicked.connect(self.reserveClear)

    def initBookinfo(self):
        self.blayout_Book = QVBoxLayout()
        self.table_reserve = QTableWidget(4, 9)
        self.table_reserve.setHorizontalHeaderLabels(["标题", "老师", "时长", "周数", "星期", "时间", "地点", "状态"
                                                         , "操作"])
        self.blayout_Book_b = QHBoxLayout()
        self.button_ReserveChange = QPushButton("执行")
        self.blayout_Book_b.addWidget(self.button_ReserveChange)
        self.blayout_Book_b.addStretch(6)
        self.frame_book = QFrame()
        self.blayout_Book.addWidget(self.table_reserve)
        self.blayout_Book.addLayout(self.blayout_Book_b)
        self.frame_book.setLayout(self.blayout_Book)
        self.button_ReserveChange.clicked.connect(self.bookOperate)

    def reserveExcute(self):
        if (self.availuableChange + self.availuableReserve) > 0:
            if (self.reseveState == 0):
                self.reseveState = 1
                self.updateCourseInfo()
                self.qtime.start(30000)
                self.button_courseExcute.setText("停止")
            else:
                self.reseveState = 0
                self.qtime.stop()
                self.button_courseExcute.setText("执行")
        else:
            QMessageBox.about(self, '警告！', '可用学时加替换学时为零!请增加替换学时或者退订！')

    def reserveClear(self):
        self.table_coursedisplay.clearContents()
        self.reserve_select_dict.clear()
        self.reserveinfoitems = 0

    def box_time_change(self):
        self.box_coursetime.clear()
        tv = self.box_course.currentText().strip()
        if tv != "Situational Dialogue":
            for key, value in self.cousetime2.items():
                self.box_coursetime.addItem(key, value)
        else:
            for key, value in self.cousetime1.items():
                self.box_coursetime.addItem(key, value)

    def addReserve(self):
        if self.reserveinfoitems < 5:
            templ = list()
            title = self.box_course.currentText()
            time = self.box_coursetime.currentText()
            weeks = self.box_week.currentText()
            days = self.box_day.currentText()
            self.table_coursedisplay.setItem(self.reserveinfoitems, 0, QTableWidgetItem(title))
            self.table_coursedisplay.setItem(self.reserveinfoitems, 1, QTableWidgetItem(time))
            self.table_coursedisplay.setItem(self.reserveinfoitems, 2, QTableWidgetItem(weeks))
            self.table_coursedisplay.setItem(self.reserveinfoitems, 3, QTableWidgetItem(days))
            templ.append(self.box_course.currentData())
            templ.append(self.box_week.currentData())
            templ.append(self.box_day.currentData())
            templ.append(self.box_coursetime.currentText())
            self.reserve_select_dict.__setitem__(self.reserveinfoitems, templ)
            self.reserveinfoitems = self.reserveinfoitems + 1

    def updateCourseInfo(self):
        now = time.asctime(time.localtime(time.time()))
        print(now)
        reslut = self.infp.Search(self.reserve_select_dict)
        if len(reslut) > 0:
            for tr in reslut:
                print(tr)

            for it in reslut:
                print("here：" + str(it[4]) + "Vs " + str(self.availuableReserve))
                if self.availuableReserve >= it[4]:
                    self.infp.reserve(it[9])
                    self.updateBookInfo()
                else:

                    if (self.availuableReserve + self.availuableChange) >= it[4]:
                        hours = it[4] - self.availuableReserve
                        changelist = self.getReplaceList(hours)
                        print("here")
                        print(changelist)
                        for ct in changelist:
                            self.infp.cancelReservation(self.bookinfopd.iloc[ct, 8])
                        self.infp.reserve(it[9])
                        self.updateBookInfo()
            if self.availuableReserve + self.availuableChange == 0:
                self.qtime.stop()
                self.reseveState = 0
                self.qtime.stop()
                self.button_courseExcute.setText("执行")

    def getReplaceList(self, num):
        result = list()
        if num == 2:
            if len(self.bookchangelist[2]) > 0:
                temp = self.bookchangelist[2]
                value = temp[0]
                result.append(value)
            if len(self.bookchangelist[1]) > 1:
                value1 = self.bookchangelist[1][0]
                value2 = self.bookchangelist[1][1]
                result.append(value1)
                result.append(value2)
        if num == 1:
            if len(self.bookchangelist[1]) > 0:
                temp = self.bookchangelist[1]
                value = temp[0]
                result.append(value)
            if len(self.bookchangelist[2]) > 0:
                temp = self.bookchangelist[2]
                value = temp[0]
                result.append(value)
        return result

    def updateBookInfo(self):
        self.bookinfodic, self.bookinfopd = self.infp.getReservationInfo()
        if "预约中" in self.bookinfodic.keys():
            self.availuableReserve = 4 - self.bookinfodic["预约中"]
        else:
            self.bookinfodic.__setitem__("预约中", 0)
            self.availuableReserve = 4
        self.booksize = len(self.bookinfopd)
        self.table_reserve.clearContents()
        if self.booksize > self.table_reserve.rowCount():
            self.table_reserve.setRowCount(self.booksize)
        for i in range(len(self.bookinfopd)):
            for j in range(8):
                tempitem = QTableWidgetItem(str(self.bookinfopd.iloc[i, j]))
                tempitem.setTextAlignment(Qt.AlignCenter)
                self.table_reserve.setItem(i, j, tempitem)
            tempcombox = QComboBox()
            tempcombox.addItem("不操作")
            if self.bookinfopd.iloc[i, 7] == "预约中":
                tempcombox.addItem("替换")
                tempcombox.addItem("退订")
            self.table_reserve.setCellWidget(i, 8, tempcombox)
        self.table_reserve.resizeColumnsToContents()
        self.status.showMessage("可用：" + str(self.availuableReserve))

    def displayCourse(self):
        print("display course")
        self.stack_center.setCurrentIndex(2)

    def displayReserve(self):
        print("display reserve")
        self.stack_center.setCurrentIndex(3)

    def displaybook(self):
        # self.table_reserve.resizeColumnsToContents()
        self.stack_center.setCurrentIndex(4)

    def bookOperate(self):
        if self.button_ReserveChange.text() == "执行":
            self.button_ReserveChange.setText("编辑")
            self.table_reserve.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.booktabledeal()
        else:
            self.button_ReserveChange.setText("执行")
            self.table_reserve.setEditTriggers(QAbstractItemView.AllEditTriggers)

    def booktabledeal(self):
        for i in range(self.booksize):
            text = self.table_reserve.cellWidget(i, 8).currentText()
            if text == "替换":
                hours = self.bookinfopd.iloc[i, 2]
                self.bookchangelist[hours].append(i)
                self.availuableChange = self.availuableReserve + self.bookinfopd.iloc[i, 2]
                self.status.showMessage("data:" + str(self.availuableReserve), 6000)
            if text == "退订":
                self.infp.cancelReservation(self.bookinfopd.iloc[i, 8])
                self.updateBookInfo()

    def login(self):
        tempurl = self.infp.getloginImg()
        self.ld = loginDisplay(tempurl)
        self.ld.accepted.connect(self.printinfo)

    def logout(self):
        self.infp.logout()
        self.islogin = 0

    def printinfo(self):
        print(self.ld.datadic)
        self.userid = self.ld.datadic["id"]
        self.password = self.ld.datadic["password"]
        self.checknum = self.ld.datadic["checknum"]
        self.userid = "SA17168009"
        self.password = "WWHFLQ"
        self.infp.login(self.userid, self.password, self.checknum)
        self.ld.close()
        self.islogin = 1
        self.updateBookInfo()

    def __del__(self):
        if self.islogin:
            self.logout()




















