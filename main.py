import os
import sys
import fs.settings
from PyQt5.QtWidgets import QApplication
from gui.file_choice import FileChoice

if __name__ == "__main__":
    app = QApplication(sys.argv)
    script_dir = os.getcwd()
    settings_manager = fs.settings.SettingsManager(".settings.pickle")

    window = FileChoice(settings_manager, script_dir)
    sys.exit(app.exec())
