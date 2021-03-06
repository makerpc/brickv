# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2015-04-10.      #
#                                                           #
# Bindings Version 2.1.4                                    #
#                                                           #
# If you have a bugfix for this file and want to commit it, #
# please fix the bug in the generator. You can find a link  #
# to the generators git repository on tinkerforge.com       #
#############################################################

#### __DEVICE_IS_NOT_RELEASED__ ####

try:
    from collections import namedtuple
except ImportError:
    try:
        from .ip_connection import namedtuple
    except ValueError:
        from ip_connection import namedtuple

try:
    from .ip_connection import Device, IPConnection, Error
except ValueError:
    from ip_connection import Device, IPConnection, Error

GetWeightCallbackThreshold = namedtuple('WeightCallbackThreshold', ['option', 'min', 'max'])
GetConfiguration = namedtuple('Configuration', ['rate', 'gain'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletLoadCell(Device):
    """
    Device for measuring weight with a load cell
    """

    DEVICE_IDENTIFIER = 253
    DEVICE_DISPLAY_NAME = 'Load Cell Bricklet'

    CALLBACK_WEIGHT = 16
    CALLBACK_WEIGHT_REACHED = 17

    FUNCTION_GET_WEIGHT = 1
    FUNCTION_SET_WEIGHT_CALLBACK_PERIOD = 2
    FUNCTION_GET_WEIGHT_CALLBACK_PERIOD = 3
    FUNCTION_SET_WEIGHT_CALLBACK_THRESHOLD = 4
    FUNCTION_GET_WEIGHT_CALLBACK_THRESHOLD = 5
    FUNCTION_SET_DEBOUNCE_PERIOD = 6
    FUNCTION_GET_DEBOUNCE_PERIOD = 7
    FUNCTION_SET_MOVING_AVERAGE = 8
    FUNCTION_GET_MOVING_AVERAGE = 9
    FUNCTION_LED_ON = 10
    FUNCTION_LED_OFF = 11
    FUNCTION_IS_LED_ON = 12
    FUNCTION_CALIBRATE = 13
    FUNCTION_SET_CONFIGURATION = 14
    FUNCTION_GET_CONFIGURATION = 15
    FUNCTION_GET_IDENTITY = 255

    THRESHOLD_OPTION_OFF = 'x'
    THRESHOLD_OPTION_OUTSIDE = 'o'
    THRESHOLD_OPTION_INSIDE = 'i'
    THRESHOLD_OPTION_SMALLER = '<'
    THRESHOLD_OPTION_GREATER = '>'

    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (2, 0, 0)

        self.response_expected[BrickletLoadCell.FUNCTION_GET_WEIGHT] = BrickletLoadCell.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLoadCell.FUNCTION_SET_WEIGHT_CALLBACK_PERIOD] = BrickletLoadCell.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletLoadCell.FUNCTION_GET_WEIGHT_CALLBACK_PERIOD] = BrickletLoadCell.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLoadCell.FUNCTION_SET_WEIGHT_CALLBACK_THRESHOLD] = BrickletLoadCell.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletLoadCell.FUNCTION_GET_WEIGHT_CALLBACK_THRESHOLD] = BrickletLoadCell.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLoadCell.FUNCTION_SET_DEBOUNCE_PERIOD] = BrickletLoadCell.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletLoadCell.FUNCTION_GET_DEBOUNCE_PERIOD] = BrickletLoadCell.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLoadCell.FUNCTION_SET_MOVING_AVERAGE] = BrickletLoadCell.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletLoadCell.FUNCTION_GET_MOVING_AVERAGE] = BrickletLoadCell.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLoadCell.FUNCTION_LED_ON] = BrickletLoadCell.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletLoadCell.FUNCTION_LED_OFF] = BrickletLoadCell.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletLoadCell.FUNCTION_IS_LED_ON] = BrickletLoadCell.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLoadCell.FUNCTION_CALIBRATE] = BrickletLoadCell.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletLoadCell.FUNCTION_SET_CONFIGURATION] = BrickletLoadCell.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletLoadCell.FUNCTION_GET_CONFIGURATION] = BrickletLoadCell.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLoadCell.CALLBACK_WEIGHT] = BrickletLoadCell.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletLoadCell.CALLBACK_WEIGHT_REACHED] = BrickletLoadCell.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletLoadCell.FUNCTION_GET_IDENTITY] = BrickletLoadCell.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletLoadCell.CALLBACK_WEIGHT] = 'I'
        self.callback_formats[BrickletLoadCell.CALLBACK_WEIGHT_REACHED] = 'h'

    def get_weight(self):
        """
        TODO
        
        If you want to get the weight periodically, it is recommended 
        to use the callback :func:`Weight` and set the period with 
        :func:`SetWeightCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletLoadCell.FUNCTION_GET_WEIGHT, (), '', 'I')

    def set_weight_callback_period(self, period):
        """
        Sets the period in ms with which the :func:`Weight` callback is triggered
        periodically. A value of 0 turns the callback off.
        
        :func:`Weight` is only triggered if the weight has changed since the
        last triggering.
        
        The default value is 0.
        """
        self.ipcon.send_request(self, BrickletLoadCell.FUNCTION_SET_WEIGHT_CALLBACK_PERIOD, (period,), 'I', '')

    def get_weight_callback_period(self):
        """
        Returns the period as set by :func:`SetWeightCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletLoadCell.FUNCTION_GET_WEIGHT_CALLBACK_PERIOD, (), '', 'I')

    def set_weight_callback_threshold(self, option, min, max):
        """
        Sets the thresholds for the :func:`WeightReached` callback. 
        
        The following options are possible:
        
        .. csv-table::
         :header: "Option", "Description"
         :widths: 10, 100
        
         "'x'",    "Callback is turned off"
         "'o'",    "Callback is triggered when the weight is *outside* the min and max values"
         "'i'",    "Callback is triggered when the weight is *inside* the min and max values"
         "'<'",    "Callback is triggered when the weight is smaller than the min value (max is ignored)"
         "'>'",    "Callback is triggered when the weight is greater than the min value (max is ignored)"
        
        The default value is ('x', 0, 0).
        """
        self.ipcon.send_request(self, BrickletLoadCell.FUNCTION_SET_WEIGHT_CALLBACK_THRESHOLD, (option, min, max), 'c h h', '')

    def get_weight_callback_threshold(self):
        """
        Returns the threshold as set by :func:`SetWeightCallbackThreshold`.
        """
        return GetWeightCallbackThreshold(*self.ipcon.send_request(self, BrickletLoadCell.FUNCTION_GET_WEIGHT_CALLBACK_THRESHOLD, (), '', 'c h h'))

    def set_debounce_period(self, debounce):
        """
        Sets the period in ms with which the threshold callback
        
        * :func:`WeightReached`
        
        is triggered, if the threshold
        
        * :func:`SetWeightCallbackThreshold`
        
        keeps being reached.
        
        The default value is 100.
        """
        self.ipcon.send_request(self, BrickletLoadCell.FUNCTION_SET_DEBOUNCE_PERIOD, (debounce,), 'I', '')

    def get_debounce_period(self):
        """
        Returns the debounce period as set by :func:`SetDebouncePeriod`.
        """
        return self.ipcon.send_request(self, BrickletLoadCell.FUNCTION_GET_DEBOUNCE_PERIOD, (), '', 'I')

    def set_moving_average(self, average):
        """
        Sets the length of a `moving averaging <http://en.wikipedia.org/wiki/Moving_average>`__ 
        for the value value.
        
        Setting the length to 1 will turn the averaging off. With less
        averaging, there is more noise on the data.
        
        The range for the averaging is 1-40.
        
        The default value is 4.
        """
        self.ipcon.send_request(self, BrickletLoadCell.FUNCTION_SET_MOVING_AVERAGE, (average,), 'B', '')

    def get_moving_average(self):
        """
        Returns the length moving average as set by :func:`SetMovingAverage`.
        """
        return self.ipcon.send_request(self, BrickletLoadCell.FUNCTION_GET_MOVING_AVERAGE, (), '', 'B')

    def led_on(self):
        """
        
        """
        self.ipcon.send_request(self, BrickletLoadCell.FUNCTION_LED_ON, (), '', '')

    def led_off(self):
        """
        
        """
        self.ipcon.send_request(self, BrickletLoadCell.FUNCTION_LED_OFF, (), '', '')

    def is_led_on(self):
        """
        
        """
        return self.ipcon.send_request(self, BrickletLoadCell.FUNCTION_IS_LED_ON, (), '', 'B')

    def calibrate(self, weight):
        """
        * 0   = set zero point
        * > 0 = set gain
        """
        self.ipcon.send_request(self, BrickletLoadCell.FUNCTION_CALIBRATE, (weight,), 'I', '')

    def set_configuration(self, rate, gain):
        """
        
        """
        self.ipcon.send_request(self, BrickletLoadCell.FUNCTION_SET_CONFIGURATION, (rate, gain), 'B B', '')

    def get_configuration(self):
        """
        rate: 0 = 10Hz
        rate: 1 = 80Hz
        gain: 0 = +-3.3*0.5V/128
        gain: 1 = +-3.3*0.5V/64
        gain: 2 = +-3.3*0.5V/32
        """
        return GetConfiguration(*self.ipcon.send_request(self, BrickletLoadCell.FUNCTION_GET_CONFIGURATION, (), '', 'B B'))

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to, 
        the position, the hardware and firmware version as well as the
        device identifier.
        
        The position can be 'a', 'b', 'c' or 'd'.
        
        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletLoadCell.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, id, callback):
        """
        Registers a callback with ID *id* to the function *callback*.
        """
        self.registered_callbacks[id] = callback

LoadCell = BrickletLoadCell # for backward compatibility
