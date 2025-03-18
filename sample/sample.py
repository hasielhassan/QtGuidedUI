
import os
import sys
from QtGuidedUI import GuidedUI

import sys
from Qt.QtWidgets import (
    QApplication, QPushButton, QTabWidget, QWidget, QVBoxLayout, QLabel
)


class MyApp(GuidedUI):
    def __init__(self):
        self.guide_config_path = os.path.join(
            os.path.dirname(__file__), "guide_config.json"
        )
        super().__init__(self.guide_config_path)
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Example Guided Application")
        self.resize(700, 400)

        layout = QVBoxLayout(self)

        # Save button
        self.btn_save = QPushButton("Save")
        self.btn_save.setObjectName("btnSave")
        layout.addWidget(self.btn_save)

        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setObjectName("mainTabs")

        # Tab 1
        self.tab_home = QWidget()
        self.tab_home_layout = QVBoxLayout()
        self.tab_home_layout.addWidget(QLabel("Home tab content"))
        self.tab_home.setLayout(self.tab_home_layout)

        # Tab 2 (Settings tab)
        self.tab_settings = QWidget()
        self.tab_settings.setObjectName("tabSettings")
        self.tab_settings_layout = QVBoxLayout()
        self.tab_settings_layout.addWidget(QLabel("Settings tab content"))
        self.tab_settings.setLayout(self.tab_settings_layout)

        # Add tabs
        self.tabs.addTab(self.tab_home, "Home")
        self.tabs.addTab(self.tab_settings, "Settings")

        layout.addWidget(self.tabs)

        # Button to trigger the guide
        self.btn_start_guide = QPushButton("Start Guide")
        self.btn_start_guide.clicked.connect(self.start_guide)
        layout.addWidget(self.btn_start_guide)

    def show_settings_tab(self):
        print("Showing settings tab...")
        self.tabs.setCurrentWidget(self.tab_settings)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
