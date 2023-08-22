"""
Test the utils module.
"""

import numpy as np
from pyfluids import FluidsList  # type: ignore

from PyNumeca.utils import boundaries


def test_boundaries():
    """Testing boundaries"""
    flow_rate = 0.19
    pt_in = 110000
    tt_in = 85

    external_diameter = 0.08
    omega = 3454

    beta_target = 1.364

    boundaries_object = boundaries.Boundaries(
        m=flow_rate, pt_in=pt_in, tt_in=tt_in, fluid=FluidsList.Nitrogen
    )

    target = np.array(
        [
            float(boundaries_object.re(omega=omega, de=external_diameter)),
            float(boundaries_object.ma(omega=omega, de=external_diameter)),
            float(boundaries_object.phi(omega, external_diameter)),
            float(
                boundaries_object.psi_b(
                    beta=beta_target, omega=omega, de=external_diameter
                )
            ),
        ]
    )
    print(target)
