from __future__ import annotations

import os
import re
import time
from typing import List, Tuple

import numpy as np
import plotly.graph_objects as go

from PyNumeca.reader.numecaParser import numecaParser


def find_between(text: str, start_keyword: str, end_keyword: str) -> list:
    return re.findall(f"(?<={start_keyword}).*?(?={end_keyword})", text, re.DOTALL)


class ArrayWithName(object):
    def __init__(self, name: str, array: np.ndarray | float):
        self.name = name
        self.array = array

    @staticmethod
    def get_curve_by_name(my_list: List["ArrayWithName"], names: List):
        for item in my_list:
            if item.name in names:
                return item


class GeomTurboParser(object):
    __impeller_wheel_name = ["Impeller_wheel", "Rotor_wheel", "row1", "impeller_wheel"]
    __cascade_wheel_name = ["Cascade_Diffuser_wheel", "Nozzle_wheel"]
    __main_blade_name = [
        "Impeller_main",
        "Rotor_main",
        "mainblade",
        "impeller_main",
        "MainBlade",
    ]
    __splitter_blade_name = ["Impeller_spl", "splitter", "splitter1"]
    __diffuser_blade_name = [
        "Cascade_Diffuser_main",
        "Nozzle_main",
        "diffuser",
        "diffuser1",
    ]
    __straight_lines_filling_points = 50

    def __init__(
        self,
        target_path: str,
        splitter_active: bool = True,
        diffuser_active: bool = True,
    ):
        if os.path.exists(target_path):
            with open(target_path) as f:
                self.raw_content = f.read()

        else:
            raise FileNotFoundError("File not found: %s" % target_path)

        self.splitter_active = splitter_active
        self.diffuser_active = diffuser_active

        (
            self.main_blade,
            self.splitter,
            self.diffuser,
            self.mb_periodicity,
            self.diff_periodicity,
        ) = self.get_blades()

        self.hub, self.shroud = self.get_channel()

    def plot_channel(self, show: bool = False) -> go.Figure:
        # Create scatter plot trace
        hub = go.Scatter(
            x=self.hub[0, :, 2],
            y=self.hub[0, :, 1],
            mode="markers+lines",
            name="Hub",
        )

        shroud = go.Scatter(
            x=self.shroud[0, :, 2],
            y=self.shroud[0, :, 1],
            mode="markers+lines",
            name="Shroud",
        )

        # Create layout
        layout = go.Layout(
            title="Channel", xaxis=dict(title="X-axis"), yaxis=dict(title="Y-axis")
        )

        # Create figure and add trace
        fig = go.Figure(data=[hub, shroud], layout=layout)

        # Display the plot
        fig.show() if show else None
        return fig

    @property
    def shape(self) -> Tuple[tuple, ...]:
        return self.main_blade.shape, self.splitter.shape, self.diffuser.shape

    def get_blades(self) -> Tuple[np.ndarray, ...]:
        self.raw_content = self.raw_content.replace(
            "NIBLADEGEOMETRY", "nibladegeometry"
        )

        blades_raw_content = find_between(
            self.raw_content, "NI_BEGIN NIBlade", "NI_END NIBlade"
        )

        if len(blades_raw_content) == 0:
            blades_raw_content = find_between(
                self.raw_content, "NI_BEGIN	NIBLADE", "NI_END	NIBLADE"
            )

            if len(blades_raw_content) == 0:
                raise ValueError("Cannot find any blade in geomTurbo file")

        wheels_raw_content = find_between(
            self.raw_content, "NI_BEGIN nirow", "NI_END nirow"
        )

        if len(wheels_raw_content) == 0:
            wheels_raw_content = find_between(
                self.raw_content, "NI_BEGIN	NIROW", "NI_END	NIROW"
            )

            if len(wheels_raw_content) == 0:
                raise ValueError("Cannot find any wheel in geomTurbo file")

        extracted_wheels = []

        for wheel in wheels_raw_content:
            name = (
                find_between(wheel, "NAME", "TYPE")[0]
                .replace(" ", "")
                .replace("\n", "")
            )

            name = name.replace("\t", "")

            try:
                periodicity = int(
                    find_between(wheel, "PERIODICITY", "ROTATION_SPEED")[0]
                    .replace(" ", "")
                    .replace("\n", "")
                )
            except:
                try:
                    periodicity = int(
                        find_between(wheel, "PERIODICITY", "\n")[0].replace("\t", "")
                    )
                except Exception as e:
                    print("cannot find row periodicity: ", e)

            extracted_wheels.append(ArrayWithName(name=name, array=periodicity))

        extracted_blades = []

        for blade in blades_raw_content:
            name = (
                find_between(blade, "NAME", "NI_BEGIN")[0]
                .replace(" ", "")
                .replace("\n", "")
            )

            if "\t" in name:
                name = name.replace("\t", "")

            blade_geom = find_between(
                blade, "NI_BEGIN nibladegeometry", "NI_END nibladegeometry"
            )

            if len(blade_geom) == 0:
                blade_geom = find_between(
                    blade, "NI_BEGIN\tnibladegeometry", "NI_END\tnibladegeometry"
                )

                if len(blade_geom) == 0:
                    raise ValueError("Cannot detect blade geometry")

            blade_geom = blade_geom[0]

            def extract_coordinates(text):
                lines = text.strip().split("\n")
                sections = []
                for i, line in enumerate(lines):
                    if "section" in line:
                        n_points = int(lines[i + 2].strip())
                        section = []
                        for j in range(n_points + 2):
                            actual_line = lines[i + j + 1]
                            if len(actual_line.strip().split()) == 3:
                                section.append(
                                    list(map(float, actual_line.strip().split()))
                                )

                        sections.append(section)
                return np.array(sections)

            suction_text = blade_geom.split("suction")[1].split("pressure")[0]
            pressure_text = blade_geom.split("suction")[1].split("pressure")[1]

            suction = extract_coordinates(suction_text)
            suction = np.concatenate(
                [suction, np.zeros(shape=(*suction.shape[:-1], 1))], axis=-1
            )
            pressure = extract_coordinates(pressure_text)
            pressure = np.flip(
                np.concatenate(
                    [pressure, np.ones(shape=(*pressure.shape[:-1], 1))], axis=-1
                ),
                axis=1,
            )

            extracted_blades.append(
                ArrayWithName(name=name, array=np.stack([suction, pressure], axis=0))
            )

        def ed(array: np.ndarray):
            return np.expand_dims(axis=0, a=array)

        main_blade = ed(
            ArrayWithName.get_curve_by_name(
                extracted_blades, self.__main_blade_name
            ).array
        )
        if self.splitter_active:
            splitter = ed(
                ArrayWithName.get_curve_by_name(
                    extracted_blades, self.__splitter_blade_name
                ).array
            )
        else:
            splitter = None

        if self.diffuser_active:
            diffuser = ed(
                ArrayWithName.get_curve_by_name(
                    extracted_blades, self.__diffuser_blade_name
                ).array
            )
        else:
            diffuser = None

        mb_periodicity = ArrayWithName.get_curve_by_name(
            extracted_wheels, self.__impeller_wheel_name
        ).array

        if self.diffuser_active:
            diff_periodicity = ArrayWithName.get_curve_by_name(
                extracted_wheels, self.__cascade_wheel_name
            ).array
        else:
            diff_periodicity = None

        return main_blade, splitter, diffuser, mb_periodicity, diff_periodicity

    def get_channel(self) -> Tuple[np.ndarray, ...]:
        channel_text = find_between(
            self.raw_content, "NI_BEGIN CHANNEL", "NI_END CHANNEL"
        )

        if len(channel_text) == 0:
            channel_text = find_between(
                self.raw_content, "NI_BEGIN\tCHANNEL", "NI_END\tCHANNEL"
            )

            if len(channel_text) == 0:
                raise ValueError("Cannot find channel in geomTurbo file")

        channel_text = channel_text[0]

        curves = find_between(
            channel_text, "NI_BEGIN basic_curve", "NI_END basic_curve"
        )

        if len(curves) == 0:
            curves = find_between(
                channel_text, "NI_BEGIN\tbasic_curve", "NI_END\tbasic_curve"
            )

        extracted_curves = []

        for curve in curves:
            name = (
                find_between(curve, "NAME", "DISCRETISATION")[0]
                .replace(" ", "")
                .replace("\n", "")
            )

            if "\t" in name:
                name = name.replace("\t", "")
            # Split the text into lines and remove the first line ("ZR")
            try:
                lines = (
                    find_between(curve, "ZR", "NI_END zrcurve")[0]
                    .strip()
                    .split("\n")[1:]
                )
            except:
                lines = (
                    find_between(curve, "ZR", "NI_END\tzrcurve")[0]
                    .strip()
                    .split("\n")[1:]
                )

            # Convert each line to a list of floats and stack them vertically to create a 2D numpy array
            array = np.vstack([np.fromstring(line, sep=" ") for line in lines])
            extracted_curves.append(ArrayWithName(name=name, array=array))

        hub_composition = find_between(
            channel_text, "NI_BEGIN channel_curve hub", "NI_END channel_curve hub"
        )

        if len(hub_composition) == 0:
            hub_composition = find_between(
                channel_text, "NI_BEGIN\tchannel_curve hub", "NI_END\tchannel_curve hub"
            )

            if len(hub_composition) == 0:
                raise ValueError("Cannot define hub curve composition")

        hub_composition = hub_composition[0]

        hub_curves = [
            f"curve_{item}"
            for item in [
                int(match.group(1))
                for match in re.finditer(r"curve_(\d+)", hub_composition)
            ]
        ]

        if len(hub_curves) == 0:
            hub_curves = [
                f"hub_crv_{item}"
                for item in [
                    int(match.group(1))
                    for match in re.finditer(r"hub_crv_(\d+)", hub_composition)
                ]
            ]

        seen = {}
        hub_curves = [seen.setdefault(x, x) for x in hub_curves if x not in seen]
        hub_arrays = [
            ArrayWithName.get_curve_by_name(extracted_curves, [item]).array
            for item in hub_curves
        ]
        hub_arrays = self.__fill_straight_curves(hub_arrays)
        hub_array = np.concatenate(hub_arrays)

        # hub_array, _ = np.unique(hub_array, axis=0, return_index=True)

        shroud_composition = find_between(
            channel_text, "NI_BEGIN channel_curve shroud", "NI_END channel_curve shroud"
        )

        if len(shroud_composition) == 0:
            shroud_composition = find_between(
                channel_text,
                "NI_BEGIN\tchannel_curve shroud",
                "NI_END\tchannel_curve shroud",
            )

            if len(shroud_composition) == 0:
                raise ValueError("Cannot define hub curve composition")

        shroud_composition = shroud_composition[0]

        shroud_curves = [
            f"curve_{item}"
            for item in [
                int(match.group(1))
                for match in re.finditer(r"curve_(\d+)", shroud_composition)
            ]
        ]

        if len(shroud_curves) == 0:
            shroud_curves = [
                f"shroud_crv_{item}"
                for item in [
                    int(match.group(1))
                    for match in re.finditer(r"shroud_crv_(\d+)", shroud_composition)
                ]
            ]

        seen = {}
        shroud_curves = [seen.setdefault(x, x) for x in shroud_curves if x not in seen]
        shroud_arrays = [
            ArrayWithName.get_curve_by_name(extracted_curves, [item]).array
            for item in shroud_curves
        ]
        shroud_arrays = self.__fill_straight_curves(shroud_arrays)
        shroud_array = np.concatenate(shroud_arrays)

        # shroud_array, _ = np.unique(shroud_array, axis=0, return_index=True)

        hub_array = np.concatenate(
            [
                np.zeros(shape=(hub_array.shape[0], 1)),
                np.flip(hub_array, axis=-1),
                np.zeros(shape=(hub_array.shape[0], 1)),
            ],
            axis=-1,
        )

        shroud_array = np.concatenate(
            [
                np.zeros(shape=(shroud_array.shape[0], 1)),
                np.flip(shroud_array, axis=-1),
                np.ones(shape=(shroud_array.shape[0], 1)),
            ],
            axis=-1,
        )

        return np.expand_dims(hub_array, axis=0), np.expand_dims(shroud_array, axis=0)

    def __fill_straight_curves(self, curves_list) -> list:
        new_curves = []
        for i, curve in enumerate(curves_list):
            if curve.shape[0] == 2:
                ref = np.array([0, 1])
                x = np.linspace(0, 1, num=self.__straight_lines_filling_points)
                r = np.interp(x, ref, curve[:, 0]).reshape(-1, 1)
                z = np.interp(x, ref, curve[:, 1]).reshape(-1, 1)

                new_curve = np.concatenate([r, z], axis=1)
            else:
                new_curve = curve

            if i != len(curves_list) - 1:
                new_curve = np.delete(new_curve, axis=0, obj=-1)

            new_curves.append(new_curve)
        return new_curves


if __name__ == "__main__":
    # target = "./tests/data/cc_autoblade.geomTurbo"
    target = "./tests/data/rotor_db.geomTurbo"
    diff_active = False
    sp_active = False

    start = time.time()
    parser = GeomTurboParser(
        target_path=target, diffuser_active=diff_active, splitter_active=sp_active
    )
    new_execution_time = time.time() - start
    print("Geomturbo reading execution time: ", new_execution_time)

    # parser.plot_channel(True)
    start = time.time()
    old_parser = numecaParser(filename=target)
    old_execution_time = time.time() - start
    print("OLD Geomturbo reading execution time: ", old_execution_time)

    print("Speedup: %.4f" % (old_execution_time / new_execution_time))

    old_mb = old_parser.exportNpyArray(0, 0)
    old_sp = old_parser.exportNpyArray(0, 1) if sp_active else None
    old_diff = old_parser.exportNpyArray(1, 0) if diff_active else None
    old_hub, old_shroud = old_parser.exportZRNpyArrays()

    parser.plot_channel(show=True)

    assert np.allclose(old_mb, parser.main_blade)
    if sp_active:
        assert np.allclose(old_sp, parser.splitter)
    if diff_active:
        assert np.allclose(old_diff, parser.diffuser)
