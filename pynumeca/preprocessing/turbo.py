import os

import joblib
import numpy as np
from pyfluids.fluids.fluid import Fluid, FluidsList

from pynumeca.postprocessing.mf import read_mf
from pynumeca.reader.numecaParser import numecaParser
from pynumeca.utils.boundaries import Boundaries
from pynumeca.utils.geometric import car2cil
from pynumeca.utils.units import convert_rotational_speed


class CentrifugalCompressor(object):
    def __init__(self, fluid: FluidsList, verbosity: bool = True):
        self.impeller = None
        self.splitter = None
        self.diffuser = None
        self.channel = None

        self.fluid = fluid

        self.rotating_speed = None
        self.external_diameter = None

        self.boundaries = None

        self.total_to_total_isentropic_efficiency = None
        self.total_to_total_pressure_ratio = None

        self.verbosity = verbosity

    def update_boundaries(self, m: float, pt_in: float, tt_in: float):
        self.boundaries = Boundaries(fluid=self.fluid, m=m, pt_in=pt_in, tt_in=tt_in)

    def load_boundaries_and_performances_from_mf(self, mf_path):
        mf_dict = read_mf(mf_path)
        self.rotating_speed = convert_rotational_speed(mf_dict["Omega"], to_rpm=False)
        self.total_to_total_isentropic_efficiency = mf_dict["Eta_tt"]
        self.total_to_total_pressure_ratio = mf_dict["Beta_tt"]

        self.update_boundaries(
            m=mf_dict["Mass_flow"], pt_in=mf_dict["Pt_in"], tt_in=mf_dict["Tt_in"]
        )

    def load_geometry_from_geomturbo(self, path: str):
        if not os.path.isfile(path):
            raise FileNotFoundError(f"{path} not found")

        parser = numecaParser()
        parser.load(filename=path)

        try:
            self.impeller = Blade(
                geometry=parser.exportNpyArray(0, 0)[0],
                periodicity=parser.get_row_periodicity(rowNumber=0),
            )
            self.external_diameter = find_external_diameter(self.impeller.geometry)

        except Exception as e:
            self.print("Cannot load impeller blade: ", e)

        try:
            self.splitter = Blade(
                geometry=parser.exportNpyArray(0, 1)[0],
                periodicity=parser.get_row_periodicity(rowNumber=0),
            )
        except Exception as e:
            self.print("Cannot load splitter blade: ", e)

        try:
            self.diffuser = Blade(
                geometry=parser.exportNpyArray(1, 0)[0],
                periodicity=parser.get_row_periodicity(rowNumber=1),
            )
        except Exception as e:
            self.print("Cannot load diffuser blade: ", e)

        try:
            hub, shroud = parser.exportZRNpyArraysList()
            self.channel = Channel(hub=hub, shroud=shroud)
        except Exception as e:
            self.print("Cannot load channel: ", e)

    def print(self, *args, **kwargs):
        print(*args, **kwargs) if self.verbosity else None

    def save(self, path: str):
        _, file_extension = os.path.splitext(path)
        if file_extension != ".bin":
            path += ".bin"

        with open(path, "wb") as f:
            joblib.dump(self, f)

        print(f"{self.__class__.__name__} saved to {path}")

    @staticmethod
    def load(path: str):
        if not os.path.exists(path):
            raise ValueError(f"{path} does not exist")
        return joblib.load(path)


class Blade(object):
    def __init__(
        self, geometry: np.ndarray, periodicity: int, is_te_blunt: bool = True
    ):
        self.geometry = geometry  # (2, S, N, 4)
        self.is_te_blunt = is_te_blunt
        self.periodicity = periodicity


class Channel(object):
    def __init__(self, hub: np.ndarray, shroud: np.ndarray):
        self.hub = hub
        self.shroud = shroud


def find_external_diameter(x):
    y = car2cil(x)
    return y[0, 0, -1, 0] * 2
