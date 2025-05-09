# -*- coding: utf-8 -*-
"""
This file contains the Qudi logic class that captures and processes fluorescence spectra.

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
import re

from qtpy import QtCore
from collections import OrderedDict
import numpy as np
import matplotlib.pyplot as plt

from core.connector import Connector
from core.statusvariable import StatusVar
from core.util.mutex import Mutex
from core.util.network import netobtain
from logic.generic_logic import GenericLogic


class SpectrumLogic(GenericLogic):

    """This logic module gathers data from the spectrometer.

    Demo config:

    spectrumlogic:
        module.Class: 'spectrum_jakob.SpectrumLogic'
        connect:
            spectrometer: 'spectrometer_3113'
            savelogic: 'savelogic'
    """

    # declare connectors
    spectrometer = Connector(interface='SpectrometerInterface')
    savelogic = Connector(interface='SaveLogic')

    # declare status variables
    _spectrum_data = StatusVar('spectrum_data', np.empty((2, 0)))

    # Internal signals
    sig_specdata_updated = QtCore.Signal()
    #sig_next_diff_loop = QtCore.Signal()

    # External signals eg for GUI module
    #spectrum_fit_updated_Signal = QtCore.Signal(np.ndarray, dict, str)
    #fit_domain_updated_Signal = QtCore.Signal(np.ndarray)

    def __init__(self, **kwargs):
        """ Create SpectrometerLogic object with connectors.

          @param dict kwargs: optional parameters
        """
        super().__init__(**kwargs)

        self.gratings = {}

        # locking for thread safety
        self.threadlock = Mutex()

    def on_activate(self):
        """ Initialisation performed during activation of the module.
        """
        # self._spectrum_data_corrected = np.array([])
        # self._calculate_corrected_spectrum()
        #
        # self.spectrum_fit = np.array([])
        # self.fit_domain = np.array([])
        #
        # self.diff_spec_data_mod_on = np.array([])
        # self.diff_spec_data_mod_off = np.array([])
        # self.repetition_count = 0    # count loops for differential spectrum

        self._spectrometer_device = self.spectrometer()
        self._save_logic = self.savelogic()

        # fetch gratings from config file of spectrometer
        for grating in self._spectrometer_device.gratings:
            groups = re.match(r'\[(\d+)nm,(\d+)]',grating).groups()
            self.gratings[f"{groups[1]:4}mm⁻¹, Blaze {groups[0]:3}nm"] = grating

        # self.sig_next_diff_loop.connect(self._loop_differential_spectrum)
        # self.sig_specdata_updated.emit()

    def on_deactivate(self):
        """ Deinitialisation performed during deactivation of the module.
        """
        if self.module_state() != 'idle' and self.module_state() != 'deactivated':
            pass
