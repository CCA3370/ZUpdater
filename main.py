import sys, os
import src.UI as UI # type: ignore
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtGui import QIcon

def get_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.normpath(os.path.join(base_path, relative_path))

if __name__ == '__main__':
    # 实例化，传参
    app = QApplication(sys.argv)
    #app.setQuitOnLastWindowClosed(False)
    # 创建对象
    mainWindow = QMainWindow()
    # 创建ui，引用文件中的Ui_MainWindow类
    
    ui = UI.Ui_MainWindow()
    # 调用Ui_MainWindow类的setupUi，创建初始组件
    ui.setupUi(mainWindow)
    # 创建窗口
    mainWindow.show()
    mainWindow.setWindowIcon(QIcon(get_path("src/logo.ico")))
    # 进入程序的主循环，并通过exit函数确保主循环安全结束(该释放资源的一定要释放)
    sys.exit(app.exec())
