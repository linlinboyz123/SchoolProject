import sys
from PyQt5 import QtWidgets
from NewStack_Manager import NewStackManager  

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = NewStackManager()  
    mainWindow.show()
    sys.exit(app.exec_())