import os, sys, zlib, math, shutil, multivolumefile, py7zr, stat, time, requests, zipfile
from urllib.request import urlretrieve, urlcleanup
from PySide6.QtWidgets import QWidget, QProgressBar, QMessageBox
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from threading import Thread
from supabase import Client, create_client
from concurrent.futures import ThreadPoolExecutor

url: str = "https://amlbkxvdtqcbpvbpcwso.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFtbGJreHZkdHFjYnB2YnBjd3NvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczNTQ2NTE5MCwiZXhwIjoyMDUxMDQxMTkwfQ.Se6Jf75Bdd89PRLZXhLkyv_mU5Q1abbPRBKPg7tKTUw"
supabase: Client = create_client(url, key)

def get_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.normpath(os.path.join(base_path, relative_path))

user_path = os.path.join(os.path.expanduser('~'), ".zupdater")

def crc(file_path, chunk_size=1024):
    crc = 0
    with open(file_path, 'rb') as file:
        while True:
            data = file.read(chunk_size)
            if not data:
                break
            crc = zlib.crc32(data, crc)
    return hex(crc & 0xFFFFFFFF)[2:].upper()

class Download(QWidget):
    def __init__(self, callback=None):
        super().__init__()
        self.callback = callback
        self.setWindowTitle("更新")
        self.setWindowIcon(QIcon(get_path("src/logo.ico")))
        self.initUI()
    def unzip_file(self, z_file, ta_dir):
        with zipfile.ZipFile(z_file, 'r') as zip_ref:
            for file in zip_ref.namelist():
                filer = os.path.split(file)[-1]
                if filer != "desktop.ini":
                    zip_ref.extract(member=file, path=ta_dir)
    def startD(self, ver=None, small=True, XP_Path=None, Mod_Path=None, lb=True, pb=True, Threads=None):
        self.show()
        self.activateWindow()
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive ) 
        self.start(ver, small, XP_Path, Mod_Path,lb,pb,Threads)
    def Schedule(self, a,b,c):
        if self.pv >= 100 :
            self.pv = 100
        else:
            self.pv = 100.0 * a * b / c
        self.pgb.setValue(self.pv)
    def update(self, per):
        self.pv = per
        self.pgb.setValue(self.pv)
    def initUI(self):
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.n = 0
        self.resize(500, 65)
        # 载入进度条控件
        self.pgb = QProgressBar(self)
        self.pgb.move(35, 20)
        self.pgb.resize(450, 22)

        # 配置一个值表示进度条的当前进度
        self.pv = 0

        # 设置进度条的范围
        self.pgb.setMinimum(0)
        self.pgb.setMaximum(0)
        self.pgb.setValue(self.pv)
    def start(self, ver=None, small=True, XP_Path=None, Mod_Path=None,lb=True,pb=True, Threads=None):
        if small == True:
            d = Thread(target=self.download_small, name="Download", args=(ver,))
        else:
            d = Thread(target=self.download_large, name="Download", args=(XP_Path,Mod_Path,lb,pb,ver,Threads))
        d.daemon = True
        d.start()
    def download_small(self, ver: str):
        try:
            ver = ver.replace(".","_")
            url = f"https://slviesjuxiojzurmxncy.supabase.co/storage/v1/object/public/Zibo/B738X_XP12_{ver}.zip"
            self.pgb.setMaximum(100)
            urlretrieve(url, os.path.join(user_path, 'temp', "B738X_UpdatePack.zip"), self.Schedule)
        except:
            QMessageBox.critical(None, '错误','网络不畅！请稍后再试。\n#21#')
            quit()
        finally:
            self.destroy()
            urlcleanup()
            self.callback()
    
    def run(self, Mod_Path, lb, pb):
        #filenames = sort_files_by_extension(get_files_with_order(archive_path))
        with multivolumefile.open(os.path.join(user_path, "temp", "B737-800X.7z"), mode='rb') as target_archive:
            with py7zr.SevenZipFile(target_archive, 'r') as archive:
                archive.extractall(os.path.split(Mod_Path)[0])
        try:
            if lb == True:
                if os.path.exists(os.path.join(user_path, 'backup', 'liveries')) == True:
                    shutil.rmtree(os.path.join(Mod_Path, 'liveries'))
                    shutil.copytree(os.path.join(user_path, 'backup', 'liveries'), os.path.join(Mod_Path, 'liveries'))
                    shutil.rmtree(os.path.join(user_path, 'backup', 'liveries'))
        except:
            pass
        try:
            if pb == True:
                if os.path.exists(os.path.join(Mod_Path, 'b738_vrconfig.txt')) == True:
                    os.unlink(os.path.join(Mod_Path, 'b738_vrconfig.txt'))
                shutil.copy(os.path.join(user_path, 'backup', 'b738_vrconfig.txt'), os.path.join(Mod_Path, 'b738_vrconfig.txt'))
        except:
            pass
        try:
            if pb == True:
                shutil.copy(os.path.join(user_path, 'backup', 'b738_prefs.txt'), os.path.join(Mod_Path, 'b738_prefs.txt'))
        except:
            pass
        try:
            os.remove(os.path.join(user_path, 'backup', 'b738_vrconfig.txt'))
        except:
            pass
        try:
            os.remove(os.path.join(user_path, 'backup', 'b738_prefs.txt'))
        except:
            pass

    def download_large(self, XP_Path, Mod_Path, lb, pb,ver,Threads):
        try:
            if Mod_Path == None:
                Mod_Path = os.path.join(XP_Path, "Aircraft", "B737-800X")
            global total
            global num
            total = 24
            num = 0
            url = f"https://3370.netlify.app/crc/crc.txt"
            urlretrieve(url, os.path.join(user_path, 'temp',"crc.txt"))
            self.pgb.setMaximum(4*total)
            global lines
            with open(os.path.join(user_path, 'temp',"crc.txt"), 'r') as c:
                lines = c.readlines()
            self.n = 0
            file_list = []
            for i in range(1,25):
                file_list.append("B737-800X.7z."+str(i).zfill(3))
            with ThreadPoolExecutor(max_workers=Threads, thread_name_prefix="MutiD") as executor:
                executor.map(self.mutiD,file_list)
        except Exception as e:
            print(e)
            QMessageBox.critical(None, '错误','网络不畅！请稍后再试。\n#22#')
            quit()
        finally:
            try:
                shutil.copytree(os.path.join(Mod_Path, 'liveries'), os.path.join(user_path, 'backup', 'liveries'))
            except:
                pass
            try:
                shutil.copyfile(os.path.join(Mod_Path, 'b738_vrconfig.txt'), os.path.join(user_path, 'backup', 'b738_vrconfig.txt'))
            except:
                pass
            try:
                shutil.copyfile(os.path.join(Mod_Path, 'b738_prefs.txt'), os.path.join(user_path, 'backup', 'b738_prefs.txt'))
            except:
                pass
            times = 0
            while True:
                times += 1
                if times >= 5:
                    QMessageBox.critical(None, '错误','权限错误！请联系开发者以获取支持！\n#28#')
                    quit()
                if not os.path.exists(Mod_Path):
                    break
                try:
                    shutil.rmtree(Mod_Path)
                except PermissionError as e:
                    err_file_path = str(e).split("\'", 2)[1]
                    if os.path.exists(err_file_path):
                        os.chmod(err_file_path, stat.S_IWUSR)
            un = Thread(target=self.run,args=(Mod_Path,lb,pb))
            un.daemon = True
            un.start()
            while un.is_alive():
                if self.n <= (4*total)-4:
                    self.n+=1
                    self.update(self.n)
                time.sleep(2)
            res = requests.get("http://106.75.62.225:7763/version?get_update")
            version = res.text
            with open(os.path.join(Mod_Path, "version.txt"), 'r') as f:
                v = f.read()
            if int(version.split(".")[2]) > int(v.split(".")[2]):
                try:
                    ver = version.replace(".","_")
                    url = f"https://slviesjuxiojzurmxncy.supabase.co/storage/v1/object/public/Zibo/B738X_XP12_{ver}.zip"
                    urlretrieve(url, os.path.join(user_path, 'temp', "B738X_UpdatePack.zip"))
                except:
                    sys.exit(1)
                finally:
                    native_crc = crc(os.path.join(user_path, 'temp', "B738X_UpdatePack.zip"))
                    try:
                        cloud_crc = requests.get("http://106.75.62.225:7763/crc?get").text
                    except:
                        QMessageBox.critical(None, '错误','网络不畅！请稍后再试。#14#')
                        quit()
                    if native_crc != cloud_crc:
                        QMessageBox.critical(None, '错误','文件校验失败！请尝试重新下载！#15#')
                        quit()
                    self.unzip_file(os.path.join(user_path, 'temp', "B738X_UpdatePack.zip"), Mod_Path)
                    os.remove(os.path.join(user_path, 'temp', "B738X_UpdatePack.zip"))
            self.n = 4*total
            self.update(self.n)
            del globals()["total"]
            del globals()["num"]
            del globals()["lines"]
            self.destroy()
            urlcleanup()
            self.callback()
    def mutiD(self,f):
        url = f"https://3370.netlify.app/full/{f}"
        while True:
            try:
                if os.path.exists(os.path.join(user_path, 'temp', f)) == False:
                    urlretrieve(url, os.path.join(user_path, 'temp', f))
                ccrc = lines[int(f[-2:])-1].replace("\n", "")
                ncrc = crc(os.path.join(user_path, 'temp', f))
                if ccrc != ncrc:
                    os.unlink(os.path.join(user_path, 'temp', f))
                else:
                    break
            except:
                pass
        self.n += 3
        self.update(self.n)