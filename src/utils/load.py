from PyQt5.QtCore import QFile, QTextStream
import os, sys

def image_base_path(filename):
    return os.path.join(os.getcwd() + "\\assets\\images\\", filename)

def load_stylesheet(filename):
    stylesheet_base_path = os.path.join(os.getcwd() + "\\assets\\css\\")
    
    qss_filename = stylesheet_base_path + filename
    qss_file = QFile(qss_filename)
    qss_file.open(QFile.ReadOnly | QFile.Text)
    qss_stream = QTextStream(qss_file)

    result = qss_stream.readAll()
    qss_file.close()

    return result