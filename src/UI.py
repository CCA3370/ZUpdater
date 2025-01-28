__version__ = '0.8.5'################

import os, sys, requests
from configparser import ConfigParser
from zipfile import ZipFile
from zlib import crc32
from PySide6.QtCore import Qt, QSize, QMetaObject, QCoreApplication
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QMessageBox
from PySide6.QtWidgets import QSizePolicy, QLineEdit, QPushButton, QGroupBox
from PySide6.QtWidgets import QComboBox, QFileDialog, QSpacerItem, QCheckBox
from PySide6.QtWidgets import QFormLayout, QCommandLinkButton
from ctypes import windll
import src.DProgress as DProgress # type: ignore
import webbrowser

windll.shell32.SetCurrentProcessExplicitAppUserModelID("3370")

config = ConfigParser()
user_path = os.path.join(os.path.expanduser('~'), ".zupdater")


def get_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.normpath(os.path.join(base_path, relative_path))

def crc(file_path, chunk_size=1024):
    crc = 0
    with open(file_path, 'rb') as file:
        while True:
            data = file.read(chunk_size)
            if not data:
                break
            crc = crc32(data, crc)
    return hex(crc & 0xFFFFFFFF)[2:].upper()


def find_path(path: str):
    for file in os.listdir(path):
        filepath = os.path.join(path, file)
        if os.path.isdir(filepath):
            find_path(filepath)
        elif file == "b738.acf" or file == 'b738_4k.acf':
            if ("Boeing 737-800" not in path.split("/")[-1]) and ("MAX" not in path.split("/")[-1]) and ("max" not in path.split("/")[-1] ) and ("Max" not in path.split("/")[-1]):
                if path not in dirlist:
                    dirlist.append(path)
    return dirlist

def unzip_file(z_file, ta_dir):
    with ZipFile(z_file, 'r') as zip_ref:
        for file in zip_ref.namelist():
            filer = os.path.split(file)[-1]
            if filer != "desktop.ini":
                zip_ref.extract(member=file, path=ta_dir)

class ImageLabel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Donate")
        self.setWindowIcon(QIcon(get_path("src/logo.ico")))
        pix = QPixmap(get_path("src/donate.png"))
        label = QLabel(self)
        label.setPixmap(pix)
        label.setScaledContents(True)  # 自适应QLabel大小
        layout = QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)

class Ui_MainWindow(QWidget):
    def init(self):
        # 检查目录是否存在
        if os.path.exists(user_path) == False:
            os.makedirs(user_path)
        if os.path.exists(os.path.join(user_path, "backup")) == False:
            os.makedirs(os.path.join(user_path, "backup"))
        if os.path.exists(os.path.join(user_path, "temp")) == False:
            os.makedirs(os.path.join(user_path, "temp"))
        if os.path.exists(os.path.join(user_path, "config.ini")) == False:
            QMessageBox.information(self.ui,'提示', '请选择X-Plane12主程序位置')
            exit, XP_path, mod_path = self.get_xppath()
            if exit == 1:
                quit()
        else:
            config.read(os.path.join(user_path, "config.ini"))
            XP_path = config.defaults()['xp_path']
            mod_path = config.defaults()['mod_path']
        config.read(os.path.join(user_path, "config.ini"))
        if not config.has_section('setting'):
            threads = '6'
            config.add_section('setting')
            config.set('setting', 'threads', threads)
            with open(os.path.join(user_path, "config.ini"), 'w') as configfile:
                config.write(configfile)
        else:
            threads = config.get('setting', 'threads')
        if os.path.exists(os.path.join(XP_path, "X-Plane.exe")) == False:# or (os.path.exists(os.path.join(mod_path, "b738.acf") and os.path.exists(os.path.join(mod_path, "b738_4k.acf")))) == False:
            QMessageBox.information(self.ui, '提示', '检测到X-Plane 12被移动，请重新选择主程序位置')
            exit, XP_path, mod_path = self.get_xppath()
            if exit == 1:
                quit()
        if (os.path.exists(os.path.join(mod_path, "b738.acf") or os.path.exists(os.path.join(mod_path, "b738_4k.acf")))) == False:
            exit, XP_path, mod_path = self.get_xppath()
            if exit == 1:
                quit()
        try:
            v = requests.get('http://106.75.62.225:7763/self_update?check').text
            ver = int(v.replace(".",''))
            if ver > int(__version__.replace(".","")):
                q = QMessageBox.question(self.ui, '自检',f'发现ZUpdater更新，前去下载？\n当前版本：v{__version__}\n最新版本：v{v}\n#版本过旧可能引起异常#', QMessageBox.Yes|QMessageBox.No,QMessageBox.No)
                if q == QMessageBox.Yes:
                    webbrowser.open("https://www.3370.tech/")
                    quit()
        except:
            pass
        return XP_path, mod_path, int(threads)
    
    def setupUi(self, MainWindow):
        self.ui = MainWindow
        donate = ImageLabel()
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(265, 440)
        MainWindow.setMinimumSize(QSize(265, 440))
        MainWindow.setMaximumSize(QSize(265, 440))
        icon = QIcon()
        icon.addFile(get_path(u"src/logo.ico"), QSize(192,192))
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QLabel(parent=self.centralwidget)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.lineEdit = QLineEdit(parent=self.centralwidget)
        self.lineEdit.setPlaceholderText("请点击 浏览 以选择目录")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit.sizePolicy().hasHeightForWidth())
        self.lineEdit.setSizePolicy(sizePolicy)
        self.lineEdit.setObjectName("lineEdit")
        self.verticalLayout.addWidget(self.lineEdit)
        self.pushButton = QPushButton(parent=self.centralwidget)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(lambda: self.get_xppath())
        self.verticalLayout.addWidget(self.pushButton)
        self.groupBox = QGroupBox(parent=self.centralwidget)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(71)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setMinimumSize(QSize(0, 90))
        self.groupBox.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)
        self.groupBox.setCheckable(True)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_2 = QLabel(parent=self.groupBox)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setMinimumSize(QSize(0, 20))
        self.label_2.setObjectName("label_2")
        self.verticalLayout_2.addWidget(self.label_2)
        self.comboBox = QComboBox(parent=self.groupBox)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(20)
        sizePolicy.setHeightForWidth(self.comboBox.sizePolicy().hasHeightForWidth())
        self.comboBox.setSizePolicy(sizePolicy)
        self.comboBox.setMinimumSize(QSize(140, 24))
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.verticalLayout_2.addWidget(self.comboBox)
        self.verticalLayout.addWidget(self.groupBox)

        self.verticalSpacer = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.groupBox_2 = QGroupBox(self.centralwidget)
        self.groupBox_2.setObjectName(u"groupBox_2")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy)
        self.groupBox_2.setMinimumSize(QSize(0, 70))
        self.groupBox_2.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)
        self.verticalLayout_3 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")

        self.checkBox_2 = QCheckBox(self.groupBox_2)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.checkBox_2.sizePolicy().hasHeightForWidth())
        self.checkBox_2.setSizePolicy(sizePolicy)
        self.checkBox_2.setObjectName("checkBox_2")
        self.verticalLayout_3.addWidget(self.checkBox_2)
        self.checkBox_3 = QCheckBox(self.groupBox_2)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.checkBox_3.sizePolicy().hasHeightForWidth())
        self.checkBox_3.setSizePolicy(sizePolicy)
        self.checkBox_3.setObjectName("checkBox_3")
        self.verticalLayout_3.addWidget(self.checkBox_3)
        self.verticalLayout.addWidget(self.groupBox_2)

        self.verticalSpacer_2 = QSpacerItem(20, 5, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout.addItem(self.verticalSpacer_2)

        self.groupBox_3 = QGroupBox(self.centralwidget)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.groupBox_3.setMinimumSize(QSize(0, 60))
        self.groupBox_3.setMaximumSize(QSize(250, 60))
        self.formLayout = QFormLayout(self.groupBox_3)
        self.formLayout.setObjectName(u"formLayout")
        self.comboBox_2 = QComboBox(self.groupBox_3)
        self.comboBox_2.setMinimumSize(QSize(80, 24))
        self.comboBox_2.setObjectName(u"comboBox_2")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.currentIndexChanged.connect(self.threads_save)
        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.comboBox_2)


        self.verticalLayout.addWidget(self.groupBox_3)

        self.commandLinkButton = QCommandLinkButton(parent=self.centralwidget)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.commandLinkButton.sizePolicy().hasHeightForWidth())
        self.commandLinkButton.setSizePolicy(sizePolicy)
        self.commandLinkButton.setIconSize(QSize(20, 20))
        self.commandLinkButton.setDefault(False)
        self.commandLinkButton.setDescription("")
        self.commandLinkButton.setObjectName("commandLinkButton")
        self.commandLinkButton.clicked.connect(lambda: donate.show())
        self.verticalLayout.addWidget(self.commandLinkButton)
        self.pushButton_2 = QPushButton(parent=self.centralwidget)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_2.sizePolicy().hasHeightForWidth())
        self.pushButton_2.setSizePolicy(sizePolicy)
        self.pushButton_2.setStyleSheet("color: rgb(0, 255, 0);")
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.clicked.connect(lambda: self.check_update(XP_Path, Mod_Path))
        self.verticalLayout.addWidget(self.pushButton_2)
        self.pushButton_3 = QPushButton(parent=self.centralwidget)
        self.pushButton_3.clicked.connect(lambda: self.Reinstall(XP_Path, Mod_Path))
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_3.sizePolicy().hasHeightForWidth())
        self.pushButton_3.setSizePolicy(sizePolicy)
        self.pushButton_3.setStyleSheet("color: rgb(255, 0, 0);")
        self.pushButton_3.setObjectName("pushButton_3")
        self.verticalLayout.addWidget(self.pushButton_3)
        MainWindow.setCentralWidget(self.centralwidget)
        XP_Path, Mod_Path, self.threads = self.init()
        self.retranslateUi(MainWindow)
        QMetaObject.connectSlotsByName(MainWindow)

    def threads_save(self):
        index = {0: "6", 1: "1", 2: "2", 3: "4", 4: "8"}
        config.read(os.path.join(user_path, "config.ini"))
        config.set("setting","threads",index[self.comboBox_2.currentIndex()])
        self.threads = int(index[self.comboBox_2.currentIndex()])
        with open(os.path.join(user_path, "config.ini"), 'w') as configfile:
            config.write(configfile)
    def check_update(self, XP_Path, Mod_Path=None):
        try:
            res = requests.get("http://106.75.62.225:7763/version?get_update")
        except:
            QMessageBox.critical(self.ui, '错误','网络不畅！请稍后再试。#13#')
            self.ui.destroy()
            quit()
        version = res.text
        try:
            with open(os.path.join(Mod_Path, "version.txt"), 'r') as f:
                v = f.read()
        except:
            q = QMessageBox.question(self.ui, '安装',f'你似乎还没有安装Zibo，或Zibo文件损坏！\n是否安装？\n###该过程耗时较长###\n最新版本：{version}', QMessageBox.Yes|QMessageBox.No,QMessageBox.Yes)
            if q == QMessageBox.Yes:
                    download_instance = DProgress.Download(callback=lambda: self.success(version))
                    try:
                        download_instance.startD(version, False, XP_Path=XP_Path, Threads=self.threads)
                    except AttributeError:
                        download_instance.startD(version, False, XP_Path=XP_Path, Threads=6)
            else:
                self.ui.destroy()
                quit()
        try:
            if int(version.split(".")[1]) != int(v.split(".")[1]):
                q = QMessageBox.question(self.ui, '更新',f'发现新版本！\n###此为大版本更新，需要全部卸载重装###\n程序将为您自动备份涂装与配置，耗时较长。\n是否安装？\n当前版本：{v}\n最新版本：{version}', QMessageBox.Yes|QMessageBox.No,QMessageBox.Yes)
                if q == QMessageBox.Yes:
                    download_instance = DProgress.Download(callback=lambda: self.success(version))
                    download_instance.startD(version, False, XP_Path, Mod_Path, Threads=self.threads)
                else:
                    self.ui.destroy()
            elif int(version.split(".")[2]) > int(v.split(".")[2]):
                q = QMessageBox.question(self.ui, '更新',f'发现新版本！此为小版本更新，是否安装？\n当前版本：{v}\n最新版本：{version}', QMessageBox.Yes|QMessageBox.No,QMessageBox.Yes)
                if q == QMessageBox.Yes:
                    download_instance = DProgress.Download(callback=lambda: self.install(version, Mod_Path))
                    download_instance.startD(version, True)
                else:
                    pass
            elif int(version.split(".")[2]) == int(v.split(".")[2]):
                QMessageBox.information(self.ui, '提示','当前Zibo已是最新版！\nEnjoy it！')
        except:
            pass
    def success(self, version):
        sys.exit(QMessageBox.information(self.ui, '提示',f'Zibo 737 {version}安装成功！\nEnjoy it！'))

    def install(self, version, Mod_path):
        native_crc = crc(os.path.join(user_path, 'temp', "B738X_UpdatePack.zip"))
        try:
            cloud_crc = requests.get("http://106.75.62.225:7763/crc?get").text
        except:
            QMessageBox.critical(self.ui, '错误','网络不畅！请稍后再试。#14#')
            return None
        if native_crc != cloud_crc:
            QMessageBox.critical(self.ui, '错误','文件校验失败！请尝试重新下载！#15#')
            quit()
        unzip_file(os.path.join(user_path, 'temp', "B738X_UpdatePack.zip"), Mod_path)
        os.remove(os.path.join(user_path, 'temp', "B738X_UpdatePack.zip"))
        QMessageBox.information(self.ui, '提示',f'Zibo 737 {version} 更新成功！\nEnjoy it！')
        self.ui.destroy()
    
    def Reinstall(self, XP_Path, Mod_Path):
        res = requests.get("http://106.75.62.225:7763/version?get_update").text
        q = QMessageBox.question(self.ui, '重装',f'危险！您正在执行重装操作！\n涂装与配置文件的备份依赖于您在主界面的选项\n重新安装将把插件更新至最新版，是否继续？\n最新版本：{res}', QMessageBox.Yes|QMessageBox.No,QMessageBox.No)
        if q == QMessageBox.Yes:
            lb = self.checkBox_2.isChecked()
            pb = self.checkBox_3.isChecked()
            download_instance = DProgress.Download(callback=lambda: self.success(res))
            download_instance.startD(res, False, XP_Path, Mod_Path, lb, pb, Threads=self.threads)
        else:
            pass

    def get_xppath(self):
        is_exist = True
        while is_exist:
            XP_path = QFileDialog.getOpenFileName(caption='请选择X-Plane 12主程序', filter='X-Plane.exe')[0].replace("X-Plane.exe","")
            if os.path.exists(os.path.join(XP_path, "X-Plane.exe")):
                is_exist = False
            elif XP_path == "":
                break
            else:
                QMessageBox.critical(self.ui, '错误','请确保您选择的路径正确\n#16#')
        if XP_path:
            search_path = os.path.join(XP_path, "Aircraft")
            global dirlist
            dirlist = []
            mod_path = find_path(search_path)
            del globals()["dirlist"]
            num = len(mod_path)
            if num > 1:
                dirs = ""
                for ds in mod_path:
                    dirs = dirs+"\n"+ds
                QMessageBox.critical(self.ui, '错误',f'在X-Plane 12中发现{num}份Zibo737，请仅保留一份！{dirs}\n#17#')
                quit()
            elif num == 0:
                config['DEFAULT'] = {'xp_Path': XP_path, 'mod_path': os.path.join(XP_path,'Aircraft','B737-800X')}
                with open(os.path.join(user_path, "config.ini"), 'w') as configfile:
                    config.write(configfile)
                self.lineEdit.setText(XP_path)
                self.check_update(XP_path,os.path.join(XP_path,'Aircraft','B737-800X'))
                return 0, "", ""
            else:
                config['DEFAULT'] = {'xp_Path': XP_path, 'mod_path': mod_path[0]}
                with open(os.path.join(user_path, "config.ini"), 'w') as configfile:
                    config.write(configfile)
                self.lineEdit.setText(XP_path)
                return 0, XP_path, mod_path[0]
        else:
            return 1, None, None
    


    def retranslateUi(self, MainWindow):
        config.read(os.path.join(user_path, "config.ini"))
        try:
            XP_path = config.defaults()['xp_path']
        except:
            XP_path = ""
        MainWindow.setWindowIcon(QIcon("./logo.ico"))
        _translate = QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "ZUpdater"))
        self.label.setText(_translate("MainWindow", "X-Plane12 主目录："))
        self.lineEdit.setText(_translate("MainWindow", XP_path))
        self.pushButton.setText(_translate("MainWindow", "浏览"))
        self.groupBox.setTitle(_translate("MainWindow", "开机自动检查更新"))
        self.label_2.setText(_translate("MainWindow", "发现新版本时："))
        self.comboBox.setItemText(0, _translate("MainWindow", "自动下载，询问安装"))
        self.comboBox.setItemText(1, _translate("MainWindow", "自动下载并安装"))
        self.comboBox.setItemText(2, _translate("MainWindow", "仅提醒"))
        self.groupBox_2.setTitle(_translate("MainWindow", "重装设置（以下选项对更新强制启用）"))
        self.checkBox_2.setText(_translate("MainWindow", "自动备份涂装"))
        self.checkBox_3.setText(_translate("MainWindow", "自动备份配置文件"))
        self.groupBox_3.setTitle(_translate("MainWindow", "下载线程数（请根据网络性能选择）"))
        self.comboBox_2.setItemText(1, _translate("MainWindow", "1"))
        self.comboBox_2.setItemText(2, _translate("MainWindow", "2"))
        self.comboBox_2.setItemText(3, _translate("MainWindow", "4"))
        self.comboBox_2.setItemText(0, _translate("MainWindow", "6（推荐）"))
        self.comboBox_2.setItemText(4, _translate("MainWindow", "8"))
        index = {1: 1, 2: 2, 4: 3, 6: 0, 8: 4}
        self.comboBox_2.setCurrentIndex(index[self.threads])
        self.commandLinkButton.setText(_translate("MainWindow", "赞助"))
        self.pushButton_2.setText(_translate("MainWindow", "检查更新"))
        self.pushButton_3.setText(_translate("MainWindow", "一键重装"))
    