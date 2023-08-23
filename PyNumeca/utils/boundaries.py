from typing import Optional

import numpy as np
import pyfluids
from pyfluids import Fluid, FluidsList, Input


class Boundaries(object):
    """
    Class representing the boundaries of a turbomachine.
    """

    update_enabled = False
    __R = 8.314462618

    def __init__(
        self,
        m: float,
        pt_in: float,
        tt_in: float,
        cp: Optional[float] = None,
        mu: Optional[float] = None,
        R: Optional[float] = None,
        fluid: Optional[pyfluids.fluids.fluid.FluidsList] = None,
    ):
        """
        Initialize the boundaries of a turbomachine.

        Parameters:
            - fluid (pyfluids.fluids.fluid.Fluid): fluid type
            - m (float): Mass flow rate
            - pt_in (float): Total pressure at the inlet of the turbomachine [Pa]
            - tt_in (float): Total temperature at the inlet of the turbomachine [K]
            - R (float): Specific gas constant
            - k (float): Specific heat ratio
            - cp (float): Specific heat at constant pressure
            - mu (float): Dynamic viscosity
        """

        self.m = m
        self.pt_in = pt_in
        self.tt_in = tt_in

        self.fluid = fluid

        if fluid is not None:
            actual_fluid = self.get_actual_fluid()

            self.cp = actual_fluid.specific_heat
            self.mu = actual_fluid.dynamic_viscosity
            self.R = self.get_gas_constant(actual_fluid)
        else:
            self.cp = cp
            self.mu = mu
            self.R = R

        self.k = self.cp / (self.cp - self.R)
        self.rho = pt_in / (self.R * tt_in)

        if isinstance(tt_in, np.ndarray):
            self.a = np.sqrt(tt_in * self.R * self.k)
        else:
            self.a = float(np.sqrt(tt_in * self.R * self.k))

        self.update_enabled = True

    def get_gas_constant(self, fluid: pyfluids.Fluid):
        return self.__R / fluid.molar_mass

    def get_actual_fluid(self):
        return Fluid(self.fluid).with_state(
            Input.pressure(self.pt_in),
            # CASTING TO CELSIUS
            Input.temperature(self.tt_in - 273.15),
        )

    def phi(self, omega: float, de: float) -> np.ndarray:
        """
        Compute the flow coefficient.

        Parameters:
            - omega (float): Angular velocity
            - de (float): Diameter of the turbomachine.

        Returns:
            - np.ndarray: The flow coefficient.
        """
        return np.array(self.m / (self.rho * omega * de**3)).reshape(-1, 1)

    def re(self, omega: float, de: float) -> np.ndarray:
        """
        Compute the Reynolds number.

        Parameters:
            - omega (float): Angular velocity
            - de (float): Diameter of the turbomachine.

        Returns:
            - np.ndarray: The Reynolds number.
        """
        return np.array(self.rho * omega * de**2 / self.mu).reshape(-1, 1)

    def ma(self, omega: float, de: float) -> np.ndarray:
        """
        Compute the Mach number.

        Parameters:
            - omega (float): Angular velocity
            - de (float): Diameter of the turbomachine.

        Returns:
            - np.ndarray: The Mach number.
        """
        return np.array(omega * de / self.a * 0.5).reshape(-1, 1)

    def psi_t(self, torque: float, omega: float, de: float, eta: float) -> float:
        """
        Compute the work coefficient.

        Parameters:
            - torque (float): Torque
            - omega (float): Angular velocity
            - de (float): Diameter of the turbomachine.
            - eta (float): Efficiency

        Returns:
            - float: The work coefficient.
        """
        return (torque * eta) / (self.m * omega * de**2)

    def psi_p(self, power: float, omega: float, de: float, eta: float) -> float:
        """
        Compute the work coefficient.

        Parameters:
            - power (float): Power
            - omega (float): Angular velocity
            - de (float): Diameter of the turbomachine.
            - eta (float): Efficiency

        Returns:
            - float: The work coefficient.
        """
        return (power * eta) / (self.m * omega**2 * de**2)

    def psi_b(self, beta: float, omega: float, de: float):
        """
        Compute the work coefficient.

        Parameters:
            - beta (float): Compression ratio
            - omega (float): Angular velocity
            - de (float): Diameter of the turbomachine.

        Returns:
            - float: The work coefficient.
        """
        return (
            self.cp
            * self.tt_in
            / ((de**2) * (omega**2))
            * (beta ** ((self.k - 1) / self.k) - 1)
        )

    def beta(self, psi_is: float, omega: float, de: float) -> float:
        """
        Compute the compression ratio.

        Parameters:
            - psi_is (float): work coefficient
            - omega (float): Angular velocity
            - de (float): Diameter of the turbomachine.

        Returns:
            - float: The compression ratio.
        """
        return (psi_is * (omega**2) * (de**2) / (self.cp * self.tt_in) + 1) ** (
            self.k / (self.k - 1)
        )
