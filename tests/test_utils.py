from PyNumeca.utils import boundaries
import numpy as np
from pyfluids import FluidsList


def test_boundaries():
    m = 0.19
    pt_in = 110000
    tt_in = 85

    R = 296.8
    k = 1.399

    cp = 1.041300e+03
    mu = 0.00003

    de = 0.08
    omega = 3454

    beta_target = 1.364

    bd = boundaries.Boundaries(m=m, pt_in=pt_in, tt_in=tt_in, R=R, k=k, cp=cp, mu=mu, fluid=FluidsList.Nitrogen)

    f = lambda x: float(x)

    target = np.array([
        f(bd.re(omega=omega, de=de)),
        f(bd.ma(omega=omega, de=de)),
        f(bd.phi(omega, de)),
        f(bd.psi_b(beta=beta_target, omega=omega, de=de))

    ])
    print(target)
    