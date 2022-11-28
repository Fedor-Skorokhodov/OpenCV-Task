from PyQt5.QtWidgets import QApplication
import windows

app = QApplication([])

window = windows.MainWindow()
window.show()

app.exec()
