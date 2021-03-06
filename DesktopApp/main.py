import sys
from functools import partial
from PyQt5 import QtCore, QtGui, QtWidgets
import qdarkstyle
from pymongo import MongoClient
from content import SetContent
from football import Ui_MainWindow


class CreateChooseWidget(QtWidgets.QWidget):

    def __init__(self, match):
        super(CreateChooseWidget, self).__init__()
        self.match_info = match
        self.name = self.match_info['match']
        self.lbl = QtWidgets.QPushButton(self.name.replace("_", " "))
        self.hbox = QtWidgets.QHBoxLayout()
        self.hbox.addWidget(self.lbl)
        self.setLayout(self.hbox)
        self.lbl.clicked.connect(partial(SetContent, self.match_info, MainWindow.ui))


class ScrollMatches(QtWidgets.QMessageBox):

    def __init__(self, all_matches, *args, **kwargs):
        QtWidgets.QMessageBox.__init__(self, *args, **kwargs)
        self.setWindowTitle("Выбор матча")
        self.setWindowIcon(QtGui.QIcon("icons/match-16.png"))
        self.button_close = self.addButton('Закрыть',
                                           QtWidgets.QMessageBox.AcceptRole)
        self.setDefaultButton(self.button_close)

        self.widgets = []
        self.content = QtWidgets.QWidget()

        self.searchbar = QtWidgets.QLineEdit()
        self.searchbar.setStyleSheet("background-image: "
                                     "url(icons/search-16.png);"
                                     "background-repeat: no-repeat; "
                                     "background-position: right;")
        self.searchbar.setPlaceholderText("Поиск по матчам")
        self.searchbar.textChanged.connect(self.update_display)

        scroll = QtWidgets.QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.content)

        self.lay = QtWidgets.QVBoxLayout(self.content)
        self.lay.addWidget(self.searchbar)
        self.completer = QtWidgets.QCompleter([x["match"].replace("_", " ")
                                               for x in all_matches])
        self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.searchbar.setCompleter(self.completer)
        for match in all_matches:
            item = CreateChooseWidget(match)
            self.lay.addWidget(item)
            self.widgets.append(item)
        spacer = QtWidgets.QSpacerItem(1, 1, QtWidgets.QSizePolicy.Minimum,
                                       QtWidgets.QSizePolicy.Expanding)
        self.lay.addItem(spacer)
        self.content.setLayout(self.lay)

        self.layout().addWidget(scroll, 0, 0, 1, self.layout().columnCount())
        self.setStyleSheet("QScrollArea{min-width:300 px; min-height: 400px}")

    def update_display(self, text):
        """
        сокрытие или показ матчей в соответствии с текстом в поисковой стркое
        """
        for widget in self.widgets:
            if text.lower() in widget.name.lower():
                widget.show()
            else:
                widget.hide()


def choose_matches_clicked():

    client = MongoClient("mongodb://localhost:27017/")
    db_conn = client["football"]
    col_conn = db_conn["gameIndicators"]
    matches = [x for x in col_conn.find({}, {"_id": 0})]
    result = ScrollMatches(matches, None)
    result.exec_()


def dark_mode():
    """
    изменение цветовой темы окна
    :yield: - тема
    """
    while True:
        MainWindow.ui.graphWidget.setBackground('#1C1C1C')
        MainWindow.ui.graphWidget2.setBackground('#1C1C1C')
        yield MainWindow.setStyleSheet("background: #1C1C1C")  # brown
        MainWindow.ui.graphWidget.setBackground('#011F36')
        MainWindow.ui.graphWidget2.setBackground('#011F36')
        yield MainWindow.setStyleSheet("background: #011F36;")  # blue
        MainWindow.ui.graphWidget.setBackground('#121e29')
        MainWindow.ui.graphWidget2.setBackground('#121e29')
        yield MainWindow.setStyleSheet("background: #121e29")  # dark_new


class MyWindow(QtWidgets.QMainWindow):
    """
    класс окна приложения, задает интерфейс и перехватывает события
    """
    def __init__(self):
        super(MyWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setup_ui(self)

    def closeEvent(self, event):
        """
        перехват события закрытия окна, вывод окна с вопросом при
        возникновении события
        :param event: - событие
        """
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle("Выход")
        msg_icon = QtGui.QIcon()
        msg_icon.addFile('icons/ball-16.png', QtCore.QSize(16, 16))
        msg.setWindowIcon(msg_icon)
        msg.setText("Вы действительно хотите выйти?")
        button_yes = msg.addButton("Да", QtWidgets.QMessageBox.AcceptRole)
        msg.addButton("Нет", QtWidgets.QMessageBox.RejectRole)
        msg.setDefaultButton(button_yes)
        msg.exec_()
        if msg.clickedButton() == button_yes:
            event.accept()
        else:
            event.ignore()

    def resizeEvent(self, event):
        """
        перехват события изменения размера окна, изменение размеров элементов
        :param event: - событие
        """
        width = self.size().width()
        height = self.size().height()
        self.ui.scroll_area.setGeometry(
            QtCore.QRect((width - 850) / 2 + 15, 0, 820, height))


if __name__ == "__main__":

    # start

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = MyWindow()

    app.setStyleSheet(qdarkstyle.load_stylesheet_pyside2())
    MainWindow.setStyleSheet("background: #121e29")
    MainWindow.show()
    # main

    MainWindow.ui.chooiseMatch.clicked.connect(choose_matches_clicked)
    MainWindow.ui.pushButton_2.clicked.connect(partial(next, (dark_mode())))

    # exit

    sys.exit(app.exec_())
