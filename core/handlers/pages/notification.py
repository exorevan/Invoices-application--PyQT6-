import typing as ty

from PyQt6 import QtCore
from PyQt6.QtCore import QPoint, Qt, QTimer
from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout, QWidget


@ty.final
class NotificationWidget(QWidget):
    def __init__(self, message: str, parent: QDialog):
        super().__init__(parent)

        # Настройка виджета
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        self.setStyleSheet(
            """
            border: 1px solid black;
            border-radius: 10px;
            padding: 15px;
            font-family: "Dubai Light";
            font-size: 17px;
            color: black;
            background-color: white;
            border-color: #6ad487;
        """
        )

        label = QLabel(message)
        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.setContentsMargins(0, 0, 0, 0)  # Убираем отступы макета
        self.setLayout(layout)
        self.adjustSize()

        # Позиционируем виджет в правом нижнем углу родительского окна
        parent_rect = parent.geometry()
        parent_bottom_right = parent.mapToGlobal(parent_rect.bottomRight())
        self.x = parent_bottom_right.x() - self.width() - 10
        self.y = parent_bottom_right.y() - self.height() - 10

        # Начальная позиция (ниже конечной)
        self.start_y = self.y + 50  # Можно изменить значение 50 на другое для настройки

        # Устанавливаем виджет на начальную позицию
        self.move(QPoint(self.x, self.start_y))

        # Показываем виджет
        self.show()

        # Используем QTimer.singleShot с нулевой задержкой для запуска анимации после отображения виджета
        QTimer.singleShot(0, self.start_animation)

        # Автоматически запускаем анимацию скрытия через 5 секунд
        QTimer.singleShot(5000, self.start_hide_animation)

    def start_animation(self):
        # Создаём анимацию появления (движение вверх)
        self.show_animation = QtCore.QPropertyAnimation(self, b"pos")
        self.show_animation.setDuration(1000)  # Длительность 500 мс, можно настроить
        self.show_animation.setStartValue(QPoint(self.x, self.start_y))
        self.show_animation.setEndValue(QPoint(self.x, self.y))
        self.show_animation.setEasingCurve(QtCore.QEasingCurve.Type.OutQuad)
        self.show_animation.start()

    def start_hide_animation(self):
        # Текущая позиция
        current_pos = self.pos()
        x = current_pos.x()
        y = current_pos.y()
        # Конечная позиция (ниже текущей)
        end_y = y + 50  # Используем то же значение, что и при появлении

        # Создаём анимацию скрытия (движение вниз)
        self.hide_animation = QtCore.QPropertyAnimation(self, b"pos")
        self.hide_animation.setDuration(200)  # Длительность 500 мс
        self.hide_animation.setStartValue(QPoint(x, y))
        self.hide_animation.setEndValue(QPoint(x, end_y))
        self.hide_animation.setEasingCurve(QtCore.QEasingCurve.Type.InQuad)
        self.hide_animation.finished.connect(
            self.close
        )  # После окончания анимации закрываем виджет
        self.hide_animation.start()

    def update_position(self):
        # Обновляем размер виджета
        self.adjustSize()
        # Получаем глобальные координаты правого нижнего угла родительского окна
        parent_rect = self.parent().geometry()
        parent_bottom_right = self.parent().mapToGlobal(parent_rect.bottomRight())
        # Вычисляем новую позицию
        x = parent_bottom_right.x() - self.width() - 10
        y = parent_bottom_right.y() - self.height() - 10
        # Перемещаем уведомление
        self.move(QPoint(x, y))
