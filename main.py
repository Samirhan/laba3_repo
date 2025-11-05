import sys
from abc import ABC, abstractmethod
from PySide6.QtCore import QPoint, QRect, Qt
from PySide6.QtGui import QPainter, QPen, QBrush, QKeySequence, QAction
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow


class IShape(ABC):
    @abstractmethod
    def draw(self, qP): ...
    @abstractmethod
    def contains(self, qP): ...
    @abstractmethod
    def set_selected(self, v): ...
    @abstractmethod
    def is_selected(self): ...


class CCircle(IShape):

    def __init__(self, x: int, y: int, radius: int = 30):
        self._center = QPoint(x, y)
        self._radius = radius
        self._selected = False

    def draw(self, p: QPainter):
        r = self._radius
        rect = QRect(self._center.x() - r, self._center.y() - r, 2 * r, 2 * r)
        if self._selected:
            p.setBrush(QBrush(Qt.darkBlue))
            p.setPen(QPen(Qt.darkBlue, 2))
        else:
            p.setBrush(QBrush(Qt.white))
            p.setPen(QPen(Qt.black, 2))
        p.drawEllipse(rect)

    def contains(self, pt):
        dx = pt.x() - self._center.x()
        dy = pt.y() - self._center.y()
        return dx * dx + dy * dy <= self._radius * self._radius

    def set_selected(self, v: bool):
        self._selected = bool(v)

    def is_selected(self):
        return self._selected


class MyStorage:

    def __init__(self):
        self._items = []
        self._iter_index = 0

    def add(self, obj: IShape):
        self._items.append(obj)

    def remove_selected(self):
        self._items = [obj for obj in self._items if not obj.is_selected()]

    def first(self):
        self._iter_index = 0

    def next(self):
        self._iter_index += 1

    def eol(self):
        return self._iter_index >= len(self._items)

    def getObject(self):
        if self.eol():
            raise IndexError("Указатель вне списка!!!!!!!!")
        return self._items[self._iter_index]

    def clear_selection(self):
        for obj in self._items:
            obj.set_selected(False)


class Canvas(QWidget):

    def __init__(self, storage):
        super().__init__()
        self._storage = storage
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMinimumSize(500, 350)
        self._base_w = 0
        self._base_h = 0

    def _ensure_base_size(self):
        if self._base_w == 0 or self._base_h == 0:
            self._base_w = self.width()
            self._base_h = self.height()

    def _scales(self):
        self._ensure_base_size()
        sx = self.width() / self._base_w
        sy = self.height() / self._base_h
        return sx, sy

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.fillRect(self.rect(), Qt.white)

        sx, sy = self._scales()
        p.scale(sx, sy)

        self._storage.first()
        while not self._storage.eol():
            self._storage.getObject().draw(p)
            self._storage.next()

    def mousePressEvent(self, e):
        if e.button() != Qt.LeftButton:
            return

        pos = e.position().toPoint()
        ctrl = bool(e.modifiers() & Qt.ControlModifier)


        sx, sy = self._scales()
        lx = int(pos.x() / sx)
        ly = int(pos.y() / sy)
        lpos = QPoint(lx, ly)

        hit_list = []
        self._storage.first()
        while not self._storage.eol():
            obj = self._storage.getObject()
            if obj.contains(lpos):
                hit_list.append(obj)
            self._storage.next()

        if not hit_list:
            self._storage.clear_selection()
            new_circle = CCircle(lpos.x(), lpos.y())
            new_circle.set_selected(True)
            self._storage.add(new_circle)
            self.update()
            return

        obj = hit_list[-1]
        if ctrl:
            obj.set_selected(not obj.is_selected())
        else:
            self._storage.clear_selection()
            obj.set_selected(True)

        self.update()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Delete:
            self._storage.remove_selected()
            self.update()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Кружочки")
        self.resize(960, 600)

        self._storage = MyStorage()

        self._canvas = Canvas(self._storage)
        self.setCentralWidget(self._canvas)

        self._add_shortcuts()

    def _add_shortcuts(self):
        act_delete = QAction(self)
        act_delete.setShortcut(QKeySequence.Delete)
        act_delete.triggered.connect(self._delete_selected)
        self.addAction(act_delete)

    def _delete_selected(self):
        self._storage.remove_selected()
        self._canvas.update()


def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
