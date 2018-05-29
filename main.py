# coding=utf-8
import sys
from PyQt5 import QtCore,QtGui, QtWidgets
from Gui import *
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ls=MainWin()
    ls.show()
    sys.exit(app.exec_())