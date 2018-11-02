from SmartHomeServer import SmartHomeServer
from PyQt5.QtWidgets import QApplication
import sys


def main():
	app = QApplication(sys.argv)
	win = SmartHomeServer()
	win.show()
	sys.exit(app.exec_())


if __name__ == '__main__':
	main()
