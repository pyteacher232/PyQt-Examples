#!/usr/bin/env python

from PyQt5.QtCore import QFile, QFileInfo, Qt
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QApplication, QHeaderView, QTableView


class FreezeTableWidget(QTableView):
    def __init__(self, model):
        # super(FreezeTableWidget, self).__init__()
        super().__init__()
        self.setModel(model)
        self.frozenTableView = QTableView(self)
        self.init()
        self.horizontalHeader().sectionResized.connect(self.updateSectionWidth)
        self.verticalHeader().sectionResized.connect(self.updateSectionHeight)
        self.frozenTableView.verticalScrollBar().valueChanged.connect(
            self.verticalScrollBar().setValue)
        self.verticalScrollBar().valueChanged.connect(
            self.frozenTableView.verticalScrollBar().setValue)

    def init(self):
        self.frozenTableView.setModel(self.model())
        self.frozenTableView.setFocusPolicy(Qt.NoFocus)
        self.frozenTableView.verticalHeader().hide()
        self.frozenTableView.horizontalHeader().setSectionResizeMode(
                QHeaderView.Fixed)
        self.viewport().stackUnder(self.frozenTableView)

        self.frozenTableView.setStyleSheet('''
            QTableView { border: none;
                         background-color: #8EDE21;
                         selection-background-color: #999;
            }''') # for demo purposes

        self.frozenTableView.setSelectionModel(self.selectionModel())
        for col in range(1, self.model().columnCount()):
            self.frozenTableView.setColumnHidden(col, True)
        self.frozenTableView.setColumnWidth(0, self.columnWidth(0))
        self.frozenTableView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.frozenTableView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.frozenTableView.show()
        self.updateFrozenTableGeometry()
        self.setHorizontalScrollMode(self.ScrollPerPixel)
        self.setVerticalScrollMode(self.ScrollPerPixel)
        self.frozenTableView.setVerticalScrollMode(self.ScrollPerPixel)

    def updateSectionWidth(self, logicalIndex, oldSize, newSize):
        if self.logicalIndex == 0:
            self.frozenTableView.setColumnWidth(0, newSize)
            self.updateFrozenTableGeometry()

    def updateSectionHeight(self, logicalIndex, oldSize, newSize):
        self.frozenTableView.setRowHeight(logicalIndex, newSize)

    def resizeEvent(self, event):
        super(FreezeTableWidget, self).resizeEvent(event)
        self.updateFrozenTableGeometry()

    def moveCursor(self, cursorAction, modifiers):
        current = super(FreezeTableWidget, self).moveCursor(cursorAction, modifiers)
        if (cursorAction == self.MoveLeft and
                self.current.column() > 0 and
                self.visualRect(current).topLeft().x() <
                    self.frozenTableView.columnWidth(0)):
            newValue = (self.horizontalScrollBar().value() +
                        self.visualRect(current).topLeft().x() -
                        self.frozenTableView.columnWidth(0))
            self.horizontalScrollBar().setValue(newValue)
        return current

    def scrollTo(self, index, hint):
        if index.column() > 0:
            super(FreezeTableWidget, self).scrollTo(index, hint)

    def updateFrozenTableGeometry(self):
        self.frozenTableView.setGeometry(
                self.verticalHeader().width() + self.frameWidth(),
                self.frameWidth(), self.columnWidth(0),
                self.viewport().height() + self.horizontalHeader().height())


def main(args):
    def split_and_strip(s, splitter):
        return [s.strip() for s in line.split(splitter)]

    app = QApplication(args)
    model = QStandardItemModel()
    file = QFile(QFileInfo(__file__).absolutePath() + '/grades.txt')
    if file.open(QFile.ReadOnly):
        line = file.readLine(200).decode('utf-8')
        header = split_and_strip(line, ',')
        model.setHorizontalHeaderLabels(header)
        row = 0
        while file.canReadLine():
            line = file.readLine(200).decode('utf-8')
            if not line.startswith('#') and ',' in line:
                fields = split_and_strip(line, ',')
                for col, field in enumerate(fields):
                    newItem = QStandardItem(field)
                    model.setItem(row, col, newItem)
                row += 1
    file.close()
    tableView = FreezeTableWidget(model)
    tableView.setWindowTitle("Frozen Column Example")
    tableView.resize(560, 680)
    tableView.show()
    return app.exec_()

if __name__ == '__main__':
    import sys
    main(sys.argv)
