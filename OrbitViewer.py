import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QDesktopWidget, QFileDialog
from PyQt5.QtGui import QPalette, QColor
import numpy as np
from typing import *
import json

import qtmodern.styles
import qtmodern.windows

from MyModules.MyWindow import Ui_MainWindow
from MyModules.Orbits import Satellite
from MyModules.MPL3Dwidget import *


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.center()

        # Create the matplotlib 3D plot
        self.plotCanvas = MplCanvas(self.plotWidget, width=5, height=5, dpi=100)
        self.toolbar = NavigationToolbar(self.plotCanvas, self.plotWidget)
        self.plotLayout.addWidget(self.plotCanvas)
        self.plotLayout.addWidget(self.toolbar)
        self.plotWidget.setLayout(self.plotLayout)

        # connect every slider to the function that handles the ploting
        sliders = [self.slider_MA, self.slider_AOP, self.slider_ECC, self.slider_INC, self.slider_LAN, self.slider_SMA]
        for slider in sliders:
            slider.sliderReleased.connect(self.slider_released)
        self.slider_released()  # Initialize the plot

        self.actionExport_to_json.triggered.connect(lambda: self.export_to_json())
        self.actionImport_from_json.triggered.connect(lambda: self.import_from_json())
        self.planet_actions = [self.actionMercury, self.actionVenus, self.actionEarth, self.actionMars,
                               self.actionJupiter, self.actionSaturn, self.actionUranus, self.actionNeptune, self.actionPluto]
        for act in self.planet_actions:
            act.triggered.connect(lambda: self.display_planets())

    def center(self):
        """ This function centers the window at launch"""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def slider_released(self):
        """ Triggered when a slider is released. Computes the new positions and plots the new graph"""
        pos = self.calculate_position(self.getSliderValues())
        self.plot(pos)

    def plot(self, pos):
        """ Handles the ploting"""
        self.plotCanvas.axes.cla()
        self.plotCanvas.axes.plot(pos[:, 0], pos[:, 1], pos[:, 2], 'o', markersize=1)
        self.plotCanvas.axes.plot([0], [0], [0], 'o', color='yellow', markersize='10')
        self.plotCanvas.axes.mouse_init(rotate_btn=1, zoom_btn=3)
        set_axes_equal(self.plotCanvas.axes)
        self.plotCanvas.fig.set_facecolor(plot_background_color)
        self.plotCanvas.axes.patch.set_facecolor(plot_face_color)
        self.plotCanvas.draw()

    def getSliderValues(self) -> List[float]:
        """ Returns the current values displayed by the sliders"""
        return [float(self.slider_SMA.value()),
                float(self.slider_INC.value()),
                float(self.slider_ECC.value()) / 1e3,
                float(self.slider_LAN.value()),
                float(self.slider_AOP.value()),
                float(self.slider_MA.value())]

    def setSliderValues(self, values: Dict[str, float]):
        self.slider_SMA.setValue(int(values['SMA']))
        self.slider_INC.setValue(int(values['INC']))
        self.slider_ECC.setValue(int(values['ECC'] * 1e3))
        self.slider_LAN.setValue(int(values['LAN']))
        self.slider_AOP.setValue(int(values['AOP']))
        self.slider_MA.setValue(int(values['MA']))
        self.slider_released()

    def calculate_position(self, values: List[float]):
        obj = Satellite(*values)
        time = np.linspace(0, obj.T, 200)
        pos = obj.orbitalparam2vectorList(time)
        return pos

    def export_to_json(self):
        """Writes the current values of the sliders to a new JSON file"""
        file_name = self.FileDialog()
        with open(file_name, 'w') as f:
            keys = ["SMA", "INC", "ECC", "LAN", "AOP", "MA"]
            values = self.getSliderValues()
            json.dump(dict(zip(keys, values)), f)

    def import_from_json(self):
        file_name = self.FileDialog(save=False)
        with open(file_name, 'r') as f:
            content = json.load(f)
            self.setSliderValues(content)

    def FileDialog(self, save=True):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        if save:
            file_name, _ = QFileDialog.getSaveFileName(
                self, "Save as", "", "JSON Files (*.json)", options=options)
        else:
            file_name, _ = QFileDialog.getOpenFileName(
                self, "Open", "", "JSON Files (*.json)", options=options)
        if file_name != '':
            if not file_name.endswith('.json'):
                file_name += '.json'
            return file_name

    def display_planets(self):
        for planet in self.planet_actions:
            if planet.isChecked():
                print('hello')


if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setStyle("Fusion")
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(51, 54, 63))
    dark_palette.setColor(QPalette.WindowText, QColor(250, 250, 250))
    dark_palette.setColor(QPalette.Base, QColor(39, 42, 49))
    dark_palette.setColor(QPalette.AlternateBase, QColor(51, 54, 63))
    dark_palette.setColor(QPalette.ToolTipBase, QColor(250, 250, 250))
    dark_palette.setColor(QPalette.ToolTipText, QColor(250, 250, 250))
    dark_palette.setColor(QPalette.Text, QColor(250, 250, 250))
    dark_palette.setColor(QPalette.Button, QColor(51, 54, 63))
    dark_palette.setColor(QPalette.ButtonText, QColor(250, 250, 250))
    dark_palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
    app.setPalette(dark_palette)
    plot_background_color = (51/255, 54/255, 63/255)
    plot_face_color = (39/255, 42/255, 49/255)

    win = MainWindow()
    mw = qtmodern.windows.ModernWindow(win)
    mw.show()

    sys.exit(app.exec_())
