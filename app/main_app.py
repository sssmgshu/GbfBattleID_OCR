# -*-coding: utf-8-*-  

"""
主にいじるメインapp  
"""
import os
import sys
import json
import configparser
import pyocr
import pyocr.builders
import pyperclip
from time import sleep
from PIL import ImageGrab, Image, ImageOps
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from area_initialize import *
from send_id_to_gs import *
from multiprocessing import Process
from multiprocessing import freeze_support

# ---- 設定ファイルの読み込み ----
# CURRENT = os.path.dirname(__file__)
# CURRENT = os.path.abspath(__file__)
CURRENT = str(pathlib.Path().resolve())
json_path = '../../setting/setting.json'
config_path = '../../setting/config.ini'
IMAGE_DIR = '../../image'
# SETTING_JSON = os.path.join(CURRENT, json_path)
SETTING_JSON = str(pathlib.Path(CURRENT + json_path).resolve())

# インストール済のTesseractのパスを通す

config = configparser.ConfigParser()
CONFIG = str(pathlib.Path(CURRENT + config_path).resolve())
config.read(CONFIG, encoding='utf-8')

# path_tesseract = "C:\\Program Files\\Tesseract-OCR"
path_tesseract = config.get('tesseract', 'tesseract')
if path_tesseract not in os.environ["PATH"].split(os.pathsep):
    os.environ["PATH"] += os.pathsep + path_tesseract

# OCRエンジンの取得
tools = pyocr.get_available_tools()
tools = tools[0]


class MainAppLayout(QDialog):
    def __init__(self, app=QApplication, parent=None):
        super(MainAppLayout, self).__init__(parent)
        self.setWindowTitle("GBF Battle ID OCR")
        self.app = app

        # ---- 並べるボタンを定義 ----
        self.button_id_input = QLineEdit()
        self.button_initialize = QPushButton('Initialize')
        self.button_initialize.clicked.connect(self.initialize_clicked)

        self.button_gs = QPushButton('Spread sheet')
        self.button_gs.clicked.connect(self.gs_clicked)
        self.button_copy = QPushButton("Copy")
        self.button_copy.clicked.connect(self.copy_clicked)
        self.button_ocr = QPushButton('Get ID')
        self.button_ocr.clicked.connect(self.ocr_clicked)
        self.button_exit = QPushButton('Exit')
        # self.button_exit.clicked.connect(self.exit_clicked)

        # ---- レイアウト定義 ----  
        LAYOUTS = []
        # レイアウト0; id
        layout_0 = QVBoxLayout()
        layout_0.addWidget(self.button_id_input)
        LAYOUTS.append(layout_0)

        # レイアウト1; 初期化, GS, コピー  
        layout_1 = QHBoxLayout()
        layout_1.addWidget(self.button_initialize)
        layout_1.addWidget(self.button_gs)
        layout_1.addWidget(self.button_copy)
        LAYOUTS.append(layout_1)
        
        # レイアウト2; 終了, 取得
        layout_2 = QHBoxLayout()
        size_policy_exit = self.button_exit.sizePolicy()
        size_policy_ocr = self.button_ocr.sizePolicy()
        
        # ストレッチを終了: 取得 = 1:3にする
        size_policy_exit.setHorizontalPolicy(1)
        size_policy_ocr.setHorizontalPolicy(3)
        self.button_exit.setSizePolicy(size_policy_exit)
        self.button_ocr.setSizePolicy(size_policy_ocr)

        layout_2.addWidget(self.button_exit)
        layout_2.addWidget(self.button_ocr)
        LAYOUTS.append(layout_2)

        # 全レイアウトの配置
        main_layout = QVBoxLayout()
        for l in LAYOUTS:
            main_layout.addLayout(l)
        self.setLayout(main_layout)

    # ---- イベント定義 ----
    def initialize_clicked(self):
        """
        Initialize をクリックしたら、OCRする位置を設定するアプリを起動する
        """
        initialize_app = Process(target=Initialize)
        initialize_app.start()
    
    def ocr_clicked(self):
        """
        設定ファイルで指定した領域内をクリッピングし、IDを取得する
        """
        self.button_id_input.clear()
        with open(SETTING_JSON, 'r') as f:
            setting_json = json.load(f)

        x1 = settig_json["x1"]
        x2 = settig_json["x2"]
        y1 = settig_json["y1"]
        y2 = settig_json["y2"]

        # image_path = os.path.join(CURRENT, os.path.join(IMAGE_DIR, 'capture.png'))
        image_path = str(pathlib.Path(CURRENT + IMAGE_DIR + 'capture.png').resolve())
        img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        img = img.resize((int(img.width * 3.5), int(img.height*3.5)))
        img.save(image_path, dpi=(300, 300))

        # OCR実行
        # IDがコピーされれば成功
        img_id = Image.open(image_path)
        img_id = img_id.convert('L')
        img_id_inv =ImageOps.invert(img_id)
        builder = pyocr.builders.TextBuilder()
        gbf_battle_id = tools.image_to_string(
            img_id_inv, lang="eng", builder=builder)
        battle_id = str(gbf_battle_id).replace(":", "")
        battle_id = battle_id.replace("-", "")
        battle_id = battle_id.replace("(", "C")
        battle_id = battle_id.replace("£", "E")
        battle_id = battle_id.replace("G", "C")
        battle_id = battle_id.replace("S", "5")
        battle_id = battle_id.replace("i", "1")
        battle_id = battle_id.replace("I", "1")
        battle_id = battle_id.replace(">", "")
        battle_id = battle_id.replace("φ", "0")
        battle_id = battle_id.replace("Φ", "0")
        

        pyperclip.copy(battle_id)
        self.button_id_input.setText(battle_id)
    
    def copy_clicked(self):
        """
        テキストボックス内のIDをクリップボードにコピーする
        """
        text_box_id = self.button_id_input.text()
        pyperclip.copy(text_box_id)

    def gs_clicked(self):
        """
        救援IDをスプレッドシートに書き込む
        """
        battle_id = self.button_id_input.text()
        try:
            send_battle_id(battle_id)
        except:
            print('Failed Update Cell.........')
        # send_battle_id(battle_id)

def main():
    app = QApplication(sys.argv)
    main_window = MainAppLayout()
    main_window.show()
    # app.exec_()
    sys.exit(app.exec_())

def start_app():
    app = Process(target=main)
    app.start()


if __name__ == "__main__":
    # exe化したときにアプリが動かない問題
    freeze_support()
    start_app()
