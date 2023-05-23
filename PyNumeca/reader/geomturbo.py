from __future__ import annotations

import os
import re
import time
from typing import List, Tuple
import numpy as np


def find_between(text: str, start_keyword: str, end_keyword: str):
    return re.findall(f'(?<={start_keyword}).*?(?={end_keyword})', text, re.DOTALL)


class ArrayWithName(object):
    def __init__(self, name: str, array: np.ndarray | float):
        self.name = name
        self.array = array

    @staticmethod
    def get_curve_by_name(my_list: List["ArrayWithName"], name: str):
        for item in my_list:
            if item.name == name:
                return item


class GeomTurboParser(object):
    __impeller_wheel_name = "Impeller_wheel"
    __cascade_wheel_name = "Cascade_Diffuser_wheel"
    __main_blade_name = "Impeller_main"
    __splitter_blade_name = "Impeller_spl"
    __diffuser_blade_name = "Cascade_Diffuser_main"
    def __init__(self,
                 target_path: str,
                 splitter_active: bool = True,
                 diffuser_active: bool = True
                 ):
        if os.path.exists(target_path):
            with open(target_path) as f:
                self.raw_content = f.read()

        else:
            raise FileNotFoundError("File not found: %s" % target_path)

        self.splitter_active = splitter_active
        self.diffuser_active = diffuser_active

        self.main_blade, self.splitter, self.diffuser, \
            self.mb_periodicity, self.diff_periodicity = self.get_blades()

        self.hub, self.shroud = self.get_channel()

        # plt.plot(self.hub[:, 0], self.hub[:, 1])
        # plt.plot(self.shroud[:, 0], self.shroud[:, 1])
        # plt.show()

    @property
    def shape(self):
        return self.main_blade.shape, self.splitter.shape, self.diffuser.shape

    def get_blades(self):
        blades_raw_content = find_between(self.raw_content,
                                          "NI_BEGIN NIBlade",
                                          "NI_END NIBlade")

        wheels_raw_content = find_between(self.raw_content,
                                          "NI_BEGIN nirow",
                                          "NI_END nirow")

        extracted_wheels = []

        for wheel in wheels_raw_content:
            name = find_between(wheel, "NAME", "TYPE")[0].replace(' ', '').replace("\n", "")
            periodicity = int(find_between(wheel, "PERIODICITY", "ROTATION_SPEED")[0].replace(' ', '').replace("\n", ""))

            extracted_wheels.append(ArrayWithName(name=name, array=periodicity))

        extracted_blades = []

        for blade in blades_raw_content:
            name = find_between(blade, "NAME", "NI_BEGIN")[0].replace(' ', '').replace("\n", "")

            blade_geom = find_between(blade,
                                      "NI_BEGIN nibladegeometry",
                                      "NI_END nibladegeometry")[0]

            def extract_coordinates(text):
                lines = text.strip().split("\n")
                sections = []
                for i, line in enumerate(lines):
                    if "section" in line:
                        n_points = int(lines[i+2].strip())
                        section = []
                        for j in range(n_points+2):
                            actual_line = lines[j + 3]
                            if len(actual_line.strip().split()) == 3:
                                section.append(list(map(float, actual_line.strip().split())))

                        sections.append(section)
                return np.array(sections)

            suction_text = blade_geom.split("suction")[1].split("pressure")[0]
            pressure_text = blade_geom.split("suction")[1].split("pressure")[1]

            suction = extract_coordinates(suction_text)
            pressure = extract_coordinates(pressure_text)

            extracted_blades.append(ArrayWithName(name=name,
                                                  array=np.stack([suction, pressure], axis=0)))


        main_blade = ArrayWithName.get_curve_by_name(extracted_blades, self.__main_blade_name).array
        if self.splitter_active:
            splitter = ArrayWithName.get_curve_by_name(extracted_blades, self.__splitter_blade_name).array
        else:
            splitter = np.empty(1)

        if self.diffuser_active:
            diffuser = ArrayWithName.get_curve_by_name(extracted_blades, self.__diffuser_blade_name).array
        else:
            diffuser = np.empty(1)

        mb_periodicity = ArrayWithName.get_curve_by_name(extracted_wheels, self.__impeller_wheel_name).array

        if self.diffuser_active:
            diff_periodicity = ArrayWithName.get_curve_by_name(extracted_wheels, self.__cascade_wheel_name).array
        else:
            diff_periodicity = np.empty(1)

        return main_blade, splitter, diffuser, mb_periodicity, diff_periodicity


    def get_channel(self) -> Tuple[np.ndarray, np.ndarray]:
        channel_text = find_between(self.raw_content, "NI_BEGIN CHANNEL", "NI_END CHANNEL")[0]

        curves = find_between(channel_text, "NI_BEGIN basic_curve", "NI_END basic_curve")

        extracted_curves = []

        for curve in curves:
            name = find_between(curve, "NAME", "DISCRETISATION")[0].replace(' ', '').replace("\n", "")
            # Split the text into lines and remove the first line ("ZR")
            lines = find_between(curve, "ZR", "NI_END zrcurve")[0].strip().split("\n")[1:]

            # Convert each line to a list of floats and stack them vertically to create a 2D numpy array
            array = np.vstack([np.fromstring(line, sep=" ") for line in lines])
            extracted_curves.append(ArrayWithName(name=name, array=array))

        hub_composition = find_between(channel_text, "NI_BEGIN channel_curve hub", "NI_END channel_curve hub")[0]
        hub_curves = [f"curve_{item}" for item in list(set([int(match.group(1)) for match in re.finditer(r"curve_(\d+)", hub_composition)]))]
        hub_arrays = [ArrayWithName.get_curve_by_name(extracted_curves, item).array for item in hub_curves]
        hub_array = np.concatenate(hub_arrays)

        shroud_composition = find_between(channel_text, "NI_BEGIN channel_curve shroud", "NI_END channel_curve shroud")[0]
        shroud_curves = [f"curve_{item}" for item in
                      list(set([int(match.group(1)) for match in re.finditer(r"curve_(\d+)", shroud_composition)]))]
        shroud_arrays = [ArrayWithName.get_curve_by_name(extracted_curves, item).array for item in shroud_curves]
        shroud_array = np.concatenate(shroud_arrays)

        return hub_array, shroud_array


if __name__ == '__main__':
    target = "tests/data/crio.geomTurbo"

    start = time.time()
    parser = GeomTurboParser(target_path=target, diffuser_active=False)
    print("Geomturbo reading execution time: ", time.time() - start)
