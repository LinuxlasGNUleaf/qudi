# -*- coding: utf-8 -*-
"""
This module contains a GUI for operating the spectrum logic module.

Qudi is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Qudi is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Qudi. If not, see <http://www.gnu.org/licenses/>.

Copyright (c) the Qudi Developers. See the COPYRIGHT.txt file at the
top-level directory of this distribution and at <https://github.com/Ulm-IQO/qudi/>
"""

import os
import time

import pyqtgraph as pg
import numpy as np
from PyQt5.QtCore import Qt, QObject

from core.connector import Connector
from core.util import units
from gui.colordefs import QudiPalettePale as palette
from gui.guibase import GUIBase
from qtpy import QtCore
from qtpy import QtWidgets
from qtpy import uic

class SpectrometerWindow(QtWidgets.QMainWindow):

    def __init__(self):
        """ Create the laser scanner window.
        """
        # Get the path to the *.ui file
        this_dir = os.path.dirname(__file__)
        ui_file = os.path.join(this_dir, 'ui_spectrometer.ui')

        # Load it
        super().__init__()
        uic.loadUi(ui_file, self)
        self.show()

class ProgressRunner(QObject):
    def __init__(self, mw):
        self._mw = mw
        super().__init__()

    def run_progress_bar(self, total_time: float):
        assert 0 < total_time
        if total_time < 2:
            steps = 5
            step_time = total_time / 5
        else:
            steps = 20
            step_time = total_time / 20

        for i in range(steps):
            self._mw.ProgressBar.setValue(i)
            self._mw.update()
            self._mw.show()
            time.sleep(step_time)


class SpectrometerGui(GUIBase):
    """
    """

    # declare connectors
    spectrumlogic = Connector(interface='SpectrumLogic')

    def __init__(self, config, **kwargs):
        super().__init__(config=config, **kwargs)
        self._spectrum_logic = None
        self._progress_runner = None
        self._progress_thread = None
        self._pw = None
        self._mw = None

    def on_activate(self):
        """ Definition and initialisation of the GUI.
        """

        self._spectrum_logic = self.spectrumlogic()

        # setting up the window
        self._mw = SpectrometerWindow()

        # set up axes of spectrum window
        self._pw = self._mw.spectrumWidget
        self._pw.setLabel('left', 'Fluorescence', units='counts/s')
        self._pw.setLabel('bottom', 'Wavelength', units='m')

        self._mw.GratingComboBox.clear()
        self._mw.GratingComboBox.addItems(self._spectrum_logic.gratings.keys())
        self.update_data()

        # Progress Runner setup
        self._progress_thread = QtCore.QThread()
        self._progress_runner = ProgressRunner(self._mw)
        self._progress_signal = QtCore.Signal(float)


        # ===> CONNECTING SIGNALS
        self._mw.GratingMoveButton.clicked.connect(self.change_grating)

        self._mw.show()

        # self._save_PNG = True

        # # Internal user input changed signals
        # self._mw.fit_domain_min_doubleSpinBox.valueChanged.connect(self.set_fit_domain)
        # self._mw.fit_domain_max_doubleSpinBox.valueChanged.connect(self.set_fit_domain)
        #
        # # Internal trigger signals
        # self._mw.do_fit_PushButton.clicked.connect(self.do_fit)
        # self._mw.fit_domain_all_data_pushButton.clicked.connect(self.reset_fit_domain_all_data)
        #
        # # fit settings
        # self._fsd = FitSettingsDialog(self._spectrum_logic.fc)
        # self._fsd.sigFitsUpdated.connect(self._mw.fit_methods_ComboBox.setFitFunctions)
        # self._fsd.applySettings()
        # self._mw.action_FitSettings.triggered.connect(self._fsd.show)

    def on_deactivate(self):
        """ Deinitialisation performed during deactivation of the module.
        """
        # disconnect signals
        # self._fsd.sigFitsUpdated.disconnect()

        self._mw.close()

    def show(self):
        """Make window visible and put it above all other windows.
        """
        QtWidgets.QMainWindow.show(self._mw)
        self._mw.activateWindow()
        self._mw.raise_()

    def change_grating(self,):
        self._progress_runner.moveToThread(self._progress_thread)
        self._progress_signal.connect(self._progress_runner.run_progress_bar)
        self._progress_thread.start()

    def update_data(self):
        """ The function that grabs the data and sends it to the plot.
        """
        data = self._spectrum_logic._spectrum_data
        #
        # # erase previous fit line
        # self._curve2.setData(x=[], y=[])
        #
        # # draw new data
        # self._curve1.setData(x=data[0, :], y=data[1, :])

    def record_single_spectrum(self):
        """ Handle resume of the scanning without resetting the data.
        """
        self._spectrum_logic.get_single_spectrum()
