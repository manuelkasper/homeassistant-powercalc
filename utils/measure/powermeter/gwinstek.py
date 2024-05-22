from __future__ import annotations

import logging
import pyvisa
import time
from typing import Any

from .errors import PowerMeterError
from .powermeter import PowerMeasurementResult, PowerMeter

_LOGGER = logging.getLogger("measure")

# Tested with GW Instek GPM-8213
class GwInstekPowerMeter(PowerMeter):
    def __init__(self, device_ip: str) -> None:
        self._device_ip = device_ip
        rm = pyvisa.ResourceManager()
        self.inst = rm.open_resource(f"ASRLsocket://{self._device_ip}:23::INSTR")

        # Configure instrument
        self.inst.write(":INPUT:MODE AC")
        self.inst.write(":INPUT:VOLTAGE:AUTO 1")
        self.inst.write(":INPUT:CURRENT:AUTO 1")
        self.inst.write(":INPUT:CFACTOR 3")
        self.inst.write(":INPUT:FILTER 1")
        self.inst.write(":MEASURE:AVERAGING:COUNT 16")
        self.inst.write(":NUMERIC:NORMAL:PRESET 1")   # output value order: U/I/P

        _LOGGER.debug("Connected to instrument %s", self.inst.query('*IDN?'))

    def get_power(self) -> PowerMeasurementResult:
        power = self.inst.query_ascii_values(":NUMERIC:NORMAL:VALUE?")[2]
        return PowerMeasurementResult(power, time.time())

    def process_answers(self, answers: dict[str, Any]) -> None:
        pass
