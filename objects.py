import sys
from qt.domanic_dialog import *
from models import *


app = QtWidgets.QApplication(sys.argv)
MainWindow = QtWidgets.QMainWindow()
ui = Ui_MainWindow()
ui.setupUi(MainWindow)

session = Session()

color_list = ['red', 'blue', 'green', 'cyan', 'magenta', 'darkRed', 'darkBlue', 'darkCyan', 'darkMagenta']

table_list = ['data_piroliz_kern', 'data_piroliz_extr', 'data_chrom_kern', 'data_chrom_extr', 'data_lit', 'data_las']