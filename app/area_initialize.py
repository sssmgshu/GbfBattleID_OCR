# -*-coding: utf-8-*-
import os
import sys
import json
import pathlib

from PyQt5 import QtWidgets, QtCore, QtGui
import tkinter as tk

json_path = '../setting/setting.json'
CURRENT = str(pathlib.Path().resolve())
SETTING_JSON = str(pathlib.Path(CURRENT + json_path).resolve())
# SETTING_JSON = os.path.join(os.path.dirname(__file__), json_path)
# SETTING_JSON = os.path.join(
#     os.path.abspath(__file__), json_path)

with open(SETTING_JSON, 'r') as f:
    settig_json = json.load(f)

# ---- 画像範囲イニシャライズ用のアプリケーション ---- 
class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        root = tk.Tk()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        self.setGeometry(0, 0, screen_width, screen_height)
        self.setWindowTitle("")
        self.setWindowOpacity(0.3)
        QtWidgets.QApplication.setOverrideCursor(
            QtGui.QCursor(QtCore.Qt.CrossCursor))
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()

        print("Initialize Area")
        self.show()

    def paintEvent(self, event):
        qp = QtGui.QPainter(self)
        qp.setPen(QtGui.QPen(QtGui.QColor("black"), 3))
        qp.setBrush(QtGui.QColor(128, 128, 255, 128))
        qp.drawRect(QtCore.QRect(self.begin, self.end))

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = self.begin
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        self.end = event.pos()
        self.close()

        x1 = min(self.begin.x(), self.end.x())
        y1 = min(self.begin.y(), self.end.y())
        x2 = max(self.begin.x(), self.end.x())
        y2 = max(self.begin.y(), self.end.y())

        # 取得した座標で設定ファイルを更新  
        settig_json["x1"] = x1
        settig_json["x2"] = x2
        settig_json["y1"] = y1
        settig_json["y2"] = y2

        with open(SETTING_JSON, 'w') as f:
            f.write(json.dumps(settig_json, ensure_ascii=False))
        

def Initialize():
    app = QtWidgets.QApplication(sys.argv)
    window = MyWidget()
    window.show()
    app.aboutToQuit.connect(app.deleteLater)
    # sys.exit(app.exec_())
    app.exec_()
    # os.remove("capture.png")


if __name__ == "__main__":
    Initialize()
