import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget
from PyQt5.QtGui import QPixmap, QPainter, QFont
from PyQt5.QtCore import QTimer, QPoint, Qt
import math
import random

class AnimatedLabel(QLabel):
    def __init__(self, background_path, object_path, targets_paths, main_window, parent=None):
        super().__init__(parent)
        self.background = QPixmap(background_path)
        self.object = QPixmap(object_path).scaled(self.background.width() // 4, self.background.height() // 4)
        self.angle = 0
        self.radius = 200
        self.center = QPoint(self.background.width() // 2, self.background.height() // 2)
        self.setFixedSize(self.background.size())

        self.targets = [QPixmap(path).scaled(50, 50) for path in targets_paths]
        self.target_positions = [QPoint(random.randint(50, self.background.width() - 50), random.randint(50, self.background.height() - 50)) for _ in self.targets]
        self.visible_targets = [True] * len(self.targets)

        self.target_index = 0
        self.moving_to_target = False
        self.returning_to_orbit = False
        self.object_position = self.center
        self.orbit_position = self.object_position
        self.last_orbit_position = self.object_position
        self.main_window = main_window

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.background)

        for i, target in enumerate(self.targets):
            if self.visible_targets[i]:
                painter.drawPixmap(self.target_positions[i], target)

        painter.drawPixmap(self.object_position, self.object)

    def update_position(self):
        speed = self.main_window.current_speed

        if self.moving_to_target and self.target_index < len(self.targets):
            target_center = QPoint(
                self.target_positions[self.target_index].x() + self.targets[self.target_index].width() // 2,
                self.target_positions[self.target_index].y() + self.targets[self.target_index].height() // 2
            )
            object_center = QPoint(
                self.object_position.x() + self.object.width() // 2,
                self.object_position.y() + self.object.height() // 2
            )
            direction = QPoint(target_center.x() - object_center.x(), target_center.y() - object_center.y())
            distance = math.sqrt(direction.x() ** 2 + direction.y() ** 2)

            if distance < 5:
                self.visible_targets[self.target_index] = False
                self.moving_to_target = False
                self.returning_to_orbit = True
                self.last_orbit_position = self.orbit_position  # Save last orbit position
                self.main_window.update_info_on_collection()
                return

            direction.setX(int(direction.x() / distance * speed))
            direction.setY(int(direction.y() / distance * speed))
            self.object_position += direction

        elif self.returning_to_orbit:
            orbit_center = QPoint(
                self.last_orbit_position.x() + self.object.width() // 2,
                self.last_orbit_position.y() + self.object.height() // 2
            )
            object_center = QPoint(
                self.object_position.x() + self.object.width() // 2,
                self.object_position.y() + self.object.height() // 2
            )
            direction = QPoint(orbit_center.x() - object_center.x(), orbit_center.y() - object_center.y())
            distance = math.sqrt(direction.x() ** 2 + direction.y() ** 2)

            if distance < 5:
                self.returning_to_orbit = False
                return

            direction.setX(int(direction.x() / distance * speed))
            direction.setY(int(direction.y() / distance * speed))
            self.object_position += direction

        else:
            self.angle = (self.angle + speed / 10) % 360
            self.orbit_position = QPoint(
                int(self.center.x() + self.radius * math.cos(math.radians(self.angle)) - self.object.width() // 2),
                int(self.center.y() + self.radius * math.sin(math.radians(self.angle)) - self.object.height() // 2)
            )
            self.object_position = self.orbit_position
            self.check_for_targets()

        self.update()

    def check_for_targets(self):
        for i, visible in enumerate(self.visible_targets):
            if visible:
                target_center = QPoint(
                    self.target_positions[i].x() + self.targets[i].width() // 2,
                    self.target_positions[i].y() + self.targets[i].height() // 2
                )
                object_center = QPoint(
                    self.object_position.x() + self.object.width() // 2,
                    self.object_position.y() + self.object.height() // 2
                )
                distance = math.sqrt((target_center.x() - object_center.x()) ** 2 + (target_center.y() - object_center.y()) ** 2)
                if distance <= 100:
                    self.target_index = i
                    self.moving_to_target = True
                    break

    def all_targets_cleared(self):
        return all(not visible for visible in self.visible_targets)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Hackathon Arayüzü")
        self.setGeometry(100, 100, 1400, 800)

        main_widget = QWidget()
        main_layout = QVBoxLayout()

        top_layout = QHBoxLayout()

        self.camera_label = QLabel()
        self.camera_label.setPixmap(QPixmap('camera.png').scaled(700, 400))
        self.camera_label.setFixedSize(700, 400)
        top_layout.addWidget(self.camera_label)

        targets_paths = [f'target{i}.png' for i in range(1, 4)]
        self.animated_label = AnimatedLabel('background.png', 'object.png', targets_paths, self)
        top_layout.addWidget(self.animated_label)

        bottom_layout = QHBoxLayout()

        self.info_label_left = QLabel()
        self.info_label_left.setFont(QFont("Arial", 12, QFont.Bold))
        self.info_label_left.setFixedSize(700, 100)
        self.info_label_left.setStyleSheet("""
            background-color: #f0f0f0;
            border: 2px solid #c0c0c0;
            border-radius: 10px;
            padding: 10px;
            """)
        bottom_layout.addWidget(self.info_label_left)

        self.info_label_right = QLabel()
        self.info_label_right.setFont(QFont("Arial", 12, QFont.Bold))
        self.info_label_right.setFixedSize(700, 100)
        self.info_label_right.setStyleSheet("""
            background-color: #f0f0f0;
            border: 2px solid #c0c0c0;
            border-radius: 10px;
            padding: 10px;
            """)
        bottom_layout.addWidget(self.info_label_right)

        main_layout.addLayout(top_layout)
        main_layout.addLayout(bottom_layout)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_info)
        self.timer.start(1000)

        self.move_timer = QTimer(self)
        self.move_timer.timeout.connect(self.animated_label.update_position)
        self.move_timer.start(50)

        self.speed_timer = QTimer(self)
        self.speed_timer.timeout.connect(self.increase_speed)
        self.speed_timer.start(10000)  # Increase speed every 10 seconds

        self.collected_trash_weight = 0
        self.filling_percentage = 50
        self.current_speed = 5  # Initial speed
        self.battery_level = 100

    def update_info(self):
        radar_tespiti = "Evet" if self.animated_label.moving_to_target else "Yok"
        doluluk_orani = self.filling_percentage
        toplanan_cop = self.collected_trash_weight

        self.info_label_left.setText(f"<b>Hız:</b> {self.current_speed * 10} km/h<br>"
                                     f"<b>Batarya:</b> %{self.battery_level}<br>"
                                     f"<b>Radar Tespiti:</b> {radar_tespiti}")
        self.info_label_right.setText(f"<b>Doluluk Oranı:</b> %{doluluk_orani}<br>"
                                      f"<b>Toplanan Çöp:</b> {toplanan_cop} kg")

        if self.battery_level > 0:
            self.battery_level -= 1  # Decrease battery level by 1% each second

    def update_info_on_collection(self):
        self.collected_trash_weight += 10  # Each collected trash weighs 10 kg
        self.filling_percentage += 10      # Filling percentage increases by 10% per trash

    def increase_speed(self):
        self.current_speed += 1  # Increase speed by 1 unit every 10 seconds

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
