# -*-coding: utf-8-*-
"""
-*- What is this?-*-
設定ファイルで指定したgoogle spread sheetの任意のセルに
inputボックスに記入された救援IDを書くスクリプト
"""

import os
import json
import pathlib
import configparser
import gspread
from oauth2client.service_account import ServiceAccountCredentials

SCOPE = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
CURRENT = str(pathlib.Path().resolve())
CONFIG_DIR = '../setting/'
config_path = '../../setting/config.ini'
def read_ini_file():
    """
    設定ファイルを読み込む
    """
    # config_file = CONFIG_DIR + 'config.ini'
    # config_path = str(pathlib.Path(CURRENT + config_file).resolve())
    CONFIG = str(pathlib.Path(CURRENT + config_path).resolve())
    config = configparser.ConfigParser()
    config.read(CONFIG, encoding='utf-8')

    credential_file = config.get('GS', 'credential_file')
    spread_sheet_key = config.get('GS', 'spread_sheet_key')
    sheet_name = config.get('GS', 'sheet_name')
    cell_name = config.get('GS', 'cell_name')

    return credential_file, spread_sheet_key, sheet_name, cell_name

def send_battle_id(battle_id):
    """
    スプレッドシートに救援IDを書き込む
    """
    # 設定ファイルの読み込みと認証情報の設定
    credential_file, spread_sheet_key, sheet_name, cell_name = read_ini_file()
    credential_path = str(pathlib.Path(CONFIG_DIR + credential_file).resolve())
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        credential_path, SCOPE)
    
    # 操作するシートを指定
    gc = gspread.authorize(credentials)
    workbook = gc.open_by_key(spread_sheet_key)
    id_sheet = workbook.worksheet(sheet_name)

    # セルの値を更新する  
    id_sheet.update_acell(cell_name, battle_id)

    print('cell updated!')

if __name__ == "__main__":
    pass









