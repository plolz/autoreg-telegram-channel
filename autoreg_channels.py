import sys
import random
import string
import asyncio
import time

from pyrogram import Client
from pyrogram.errors import FloodWait
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QTextEdit, QLineEdit, QLabel
)
from PyQt6.QtCore import QThread, pyqtSignal

#api_id и api_hash
api_id = 26793270
api_hash = "43be6adfd76ddf2e826b19c5e7235b3a"

SESSION_NAME = "my_session"


class ChannelCreatorThread(QThread):
    log = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, count):
        super().__init__()
        self.count = count

    def random_name(self):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=10))

    def run(self):
       
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.create_channels())

    async def create_channels(self):
        async with Client(SESSION_NAME, api_id=api_id, api_hash=api_hash) as app:
            self.log.emit("✅ Успешный вход в Telegram")
            for i in range(self.count):
                name = self.random_name()
                try:
                    await app.create_channel(title=name, description="Автоканал")
                    self.log.emit(f"[{i + 1}] ✅ Канал создан: {name}")
                except FloodWait as e:
                    self.log.emit(f"[{i + 1}] ⏳ FloodWait: ждём {e.value} секунд...")
                    await asyncio.sleep(e.value)
                    continue
                except Exception as e:
                    self.log.emit(f"[{i + 1}] ❌ Ошибка: {e}")
                if i < self.count - 1:
                    self.log.emit("⏳ Ожидание 15 сек перед следующим...")
                    await asyncio.sleep(15)
            self.log.emit("🏁 Создание завершено.")
            self.finished.emit()


class ChannelCreatorGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("авторегер каналов")
        self.setGeometry(300, 300, 400, 450)
        self.setStyleSheet("background-color: #2e2e2e; color: white; font-size: 14px; border-radius: 10px;")

        self.layout = QVBoxLayout(self)

        self.label = QLabel("🔢 Кол-во каналов:")
        self.label.setStyleSheet("padding: 4px;")
        self.input = QLineEdit()
        self.input.setPlaceholderText("Например: 5")
        self.input.setStyleSheet("padding: 8px; border-radius: 6px;")
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.input)

        self.start_btn = QPushButton("🚀 Начать создание")
        self.start_btn.setStyleSheet("background-color: #3a8dff; padding: 10px; border-radius: 8px;")
        self.start_btn.clicked.connect(self.start_creation)
        self.layout.addWidget(self.start_btn)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setStyleSheet("background-color: #1e1e1e; color: white; border-radius: 6px; padding: 6px;")
        self.layout.addWidget(self.log_box)

    def append_log(self, text):
        self.log_box.append(text)

    def start_creation(self):
        try:
            count = int(self.input.text())
            if count <= 0:
                raise ValueError
        except ValueError:
            self.append_log("❗ Введите корректное число каналов.")
            return

        self.start_btn.setEnabled(False)
        self.append_log("🔐 Вход в Telegram...")

        self.worker = ChannelCreatorThread(count)
        self.worker.log.connect(self.append_log)
        self.worker.finished.connect(self.creation_finished)
        self.worker.start()

    def creation_finished(self):
        self.append_log("✅ Все каналы созданы.")
        self.start_btn.setEnabled(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChannelCreatorGUI()ы
    window.show()
    sys.exit(app.exec())
