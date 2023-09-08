import re
from collections import OrderedDict
from copy import copy, deepcopy

import numpy as np

from pynumeca.reader.iecEntry import iecEntry
from pynumeca.reader.iecGroup import iecGroup
from pynumeca.reader.niBladeGeometryEntry import niBladeGeometryEntry
from pynumeca.reader.zrCurveEntry import zrCurveEntry


class numecaParser(OrderedDict):
    def __init__(self, filename=""):
        super().__init__()
        self.fileName = filename
        self.stringData = ""

        if filename != "":
            self.load(filename)
            self.parsing()

    def load(self, filename):
        self.fileName = filename
        try:
            with open(self.fileName, "r") as file:
                self.stringData = file.readlines()
        except Exception as e:
            self.error_notification(e)
        self.parsing()

    def extract_d3d_parameters_string(self):
        output_string = ""
        try:
            number_of_parameters = self["ROOT"]["DESIGN3D_COMPUTATION_0"][
                "DATABASE_GENERATION_MINAMO_0"
            ]["SIMULATION_TASK_MANAGER_0"]["SIMULATION_TASKS_0"][
                "SIMULATION_TASK_PARAM_GEOM_MODEL_0"
            ][
                "PARAMETRIC_LAYER_0"
            ][
                "PARAMETERS_0"
            ][
                "NUMBER_OF_PARAMETERS"
            ].value

            output_string += number_of_parameters + "\n"

            for key, value in self["ROOT"]["DESIGN3D_COMPUTATION_0"][
                "DATABASE_GENERATION_MINAMO_0"
            ]["SIMULATION_TASK_MANAGER_0"]["SIMULATION_TASKS_0"][
                "SIMULATION_TASK_PARAM_GEOM_MODEL_0"
            ][
                "PARAMETRIC_LAYER_0"
            ][
                "PARAMETERS_0"
            ].items():
                if "PARAMETER_" in key:
                    output_string += value["NAME"].value + "\n"

            return output_string

        except Exception as e:
            raise CustomError

    def extract_d3d_parameters_list(self):
        output_list = []
        try:
            for key, value in self["ROOT"]["DESIGN3D_COMPUTATION_0"][
                "DATABASE_GENERATION_MINAMO_0"
            ]["SIMULATION_TASK_MANAGER_0"]["SIMULATION_TASKS_0"][
                "SIMULATION_TASK_PARAM_GEOM_MODEL_0"
            ][
                "PARAMETRIC_LAYER_0"
            ][
                "PARAMETERS_0"
            ].items():
                if "PARAMETER_" in key:
                    output_list.append(value["NAME"].value)

            return output_list
        except Exception as e:
            raise CustomError

    def create_d3d_default_parameter(self):
        stringlist = []
        stringlist.append("                     NI_BEGIN\tPARAMETER\n")
        stringlist.append(
            "                        NAME                           DEFAULT\n"
        )
        stringlist.append(
            "                        PARAMETRIC_TYPE                DOUBLE\n"
        )
        stringlist.append(
            "                        LIMIT_MIN                      -1000000000\n"
        )
        stringlist.append(
            "                        LIMIT_MAX                      1000000000\n"
        )
        stringlist.append(
            "                        VALUE                          0.002\n"
        )
        stringlist.append(
            "                        VALUE_MIN                      0.001\n"
        )
        stringlist.append(
            "                        VALUE_MAX                      0.003\n"
        )
        stringlist.append("                        VALUE_REF                      1\n")
        stringlist.append("                        NB_LEVELS                      2\n")
        stringlist.append(
            "                        QUANTITY_TYPE                  VALUE\n"
        )
        stringlist.append(
            "                        UNCERTAIN                      FALSE\n"
        )
        stringlist.append(
            "                        REDUCTION                      FALSE\n"
        )
        stringlist.append("                     NI_END\tPARAMETER\n")
        return self.deepTree(stringlist, 0)

    def create_d3d_parameter(self, name, type, value, min=None, max=None):
        new_parameter, _ = self.create_d3d_default_parameter()
        new_parameter["NAME"].value = name
        new_parameter["PARAMETRIC_TYPE"].value = type
        new_parameter["VALUE"].value = value
        if min is not None and max is not None:
            new_parameter["VALUE_MIN"].value = min
            new_parameter["VALUE_MAX"].value = max
        else:
            new_parameter["VALUE_MIN"].value = value
            new_parameter["VALUE_MAX"].value = value
        return new_parameter

    def add_d3d_parameter(self, *arg):
        parameters_layer = self["ROOT"]["DESIGN3D_COMPUTATION_0"][
            "DATABASE_GENERATION_MINAMO_0"
        ]["SIMULATION_TASK_MANAGER_0"]["SIMULATION_TASKS_0"][
            "SIMULATION_TASK_PARAM_GEOM_MODEL_0"
        ][
            "PARAMETRIC_LAYER_0"
        ][
            "PARAMETERS_0"
        ]

        if len(arg) == 1 and isinstance(arg[0], iecGroup):
            new_parameter = arg[0]
        elif len(arg) == 3:
            new_parameter = self.create_d3d_parameter(arg[0], arg[1], arg[2])
        elif len(arg) == 5:
            new_parameter = self.create_d3d_parameter(
                arg[0], arg[1], arg[2], arg[3], arg[4]
            )
        else:
            raise CustomError

        number_of_parameters = parameters_layer["NUMBER_OF_PARAMETERS"].value
        new_number_of_parameters = str(int(number_of_parameters) + 1)
        parameters_layer["NUMBER_OF_PARAMETERS"].value = new_number_of_parameters

        n = 0
        new_group_name = "PARAMETER" + "_" + str(n)
        while new_group_name in parameters_layer:
            n += 1
            new_group_name = "PARAMETER" + "_" + str(n)

        self["ROOT"]["DESIGN3D_COMPUTATION_0"]["DATABASE_GENERATION_MINAMO_0"][
            "SIMULATION_TASK_MANAGER_0"
        ]["SIMULATION_TASKS_0"]["SIMULATION_TASK_PARAM_GEOM_MODEL_0"][
            "PARAMETRIC_LAYER_0"
        ][
            "PARAMETERS_0"
        ] = self.insert_key_value(
            parameters_layer, new_group_name, "NI_END_PARAMETERS", new_parameter
        )

    def remove_d3d_parameter(self, number=None):
        parameters_layer = self["ROOT"]["DESIGN3D_COMPUTATION_0"][
            "DATABASE_GENERATION_MINAMO_0"
        ]["SIMULATION_TASK_MANAGER_0"]["SIMULATION_TASKS_0"][
            "SIMULATION_TASK_PARAM_GEOM_MODEL_0"
        ][
            "PARAMETRIC_LAYER_0"
        ][
            "PARAMETERS_0"
        ]
        number_of_parameters = parameters_layer["NUMBER_OF_PARAMETERS"].value

        if int(number_of_parameters) > 0 and number is None:
            new_number_of_parameters = str(int(number_of_parameters) - 1)
            parameters_layer["NUMBER_OF_PARAMETERS"].value = new_number_of_parameters

            n = 0
            last_group_name = "PARAMETER" + "_" + str(n)
            while last_group_name in parameters_layer:
                n += 1
                last_group_name = "PARAMETER" + "_" + str(n)
            n -= 1
            last_group_name = "PARAMETER" + "_" + str(n)

            self["ROOT"]["DESIGN3D_COMPUTATION_0"]["DATABASE_GENERATION_MINAMO_0"][
                "SIMULATION_TASK_MANAGER_0"
            ]["SIMULATION_TASKS_0"]["SIMULATION_TASK_PARAM_GEOM_MODEL_0"][
                "PARAMETRIC_LAYER_0"
            ][
                "PARAMETERS_0"
            ].pop(
                last_group_name
            )

        elif int(number_of_parameters) > 0 and (
            isinstance(number, int) or isinstance(number, str)
        ):
            new_number_of_parameters = str(int(number_of_parameters) - 1)
            parameters_layer["NUMBER_OF_PARAMETERS"].value = new_number_of_parameters

            if str(number).isdigit():
                last_group_name = "PARAMETER" + "_" + str(number)
            elif number in self.extract_d3d_parameters_list():
                last_group_name = ""
                for key, value in parameters_layer.items():
                    if "PARAMETER_" in key and number == value["NAME"].value:
                        last_group_name = key
            else:
                raise CustomError

            self["ROOT"]["DESIGN3D_COMPUTATION_0"]["DATABASE_GENERATION_MINAMO_0"][
                "SIMULATION_TASK_MANAGER_0"
            ]["SIMULATION_TASKS_0"]["SIMULATION_TASK_PARAM_GEOM_MODEL_0"][
                "PARAMETRIC_LAYER_0"
            ][
                "PARAMETERS_0"
            ].pop(
                last_group_name
            )

        else:
            pass

    @staticmethod
    def insert_key_value(a_dict, key, pos_key, value):
        new_dict = iecGroup()
        for k, v in a_dict.items():
            if k == pos_key:
                new_dict[key] = value  # insert new key
            new_dict[k] = v
        return new_dict

    def parsing(self):
        if isinstance(self.stringData, list) and "GEOMETRY TURBO" in self.stringData[0]:
            self.stringData[0] = "GEOMETRY-TURBO\n"
        self["ROOT"], temp = self.deepTree(self.stringData, 0)
        self["ROOT"] = self.deep_reorder_zrcurve(self["ROOT"])
        # self.merge_ZR()
        self.cleanUnusedBasicCurves()

    def deep_reorder_zrcurve(self, group):
        new_group = iecGroup()
        for key, value in group.items():
            if isinstance(value, iecGroup) and "zrcurve" in (list(value.items()))[0][0]:
                new_group[key] = zrCurveEntry(value)
            elif isinstance(value, iecGroup) and any(
                x in (list(value.items()))[0][0]
                for x in ["nibladegeometry", "NIBLADEGEOMETRY"]
            ):
                new_group[key] = niBladeGeometryEntry(value)
                # print (key)
                # new_group[key] = self.deepReorderZRcurve(value)
            #    new_group[key] = niBladeGeometryEntry(value)
            elif isinstance(value, iecGroup):
                new_group[key] = self.deep_reorder_zrcurve(value)
            else:
                new_group[key] = value
        return new_group

    def deepTree(self, string_data, line_index):
        newcall = True
        group = iecGroup()
        while line_index < len(string_data):
            line_string = string_data[line_index]
            entry = iecEntry()
            entry.parseSimpleEntry(line_string)
            if newcall and "NI_BEGIN" in line_string:
                # key = entry.key + "_" + entry.value
                if isinstance(entry.value, list):
                    key = entry.key + "_" + entry.tag + "_" + entry.value[0]
                else:
                    key = entry.key + "_" + entry.value
                group[key] = entry
                newcall = False
                line_index += 1
            elif line_index == 0 and entry.key == "GEOMETRY-TURBO":
                string_data[0] = "GEOMETRY TURBO\n"
                group_name = "GEOMTURBO"
                group[group_name], line_index = self.deepTree(string_data, line_index)
            elif line_index == 0 and entry.value == "TURBO":
                key = entry.key + "_" + entry.value
                group[key] = entry
                newcall = False
                line_index += 1
            elif not newcall and "NI_BEGIN" in line_string:
                n = 0
                if isinstance(entry.value, list):
                    group_name = entry.tag + "_" + entry.value[0] + "_" + str(n)
                else:
                    group_name = entry.value + "_" + str(n)
                while group_name in group:
                    n += 1
                    if isinstance(entry.value, list):
                        group_name = entry.tag + "_" + entry.value[0] + "_" + str(n)
                    else:
                        group_name = entry.value + "_" + str(n)

                group[group_name], line_index = self.deepTree(string_data, line_index)
            elif "NI_END" in line_string:
                key = entry.key + "_" + entry.value
                group[key] = entry
                newcall = False
                line_index += 1
                return group, line_index
            elif line_string.lstrip(" ").startswith(("*", "#")):
                n = 0
                key = "comment" + "_" + str(n)
                while key in group:
                    n += 1
                    key = "comment_" + str(n)
                group[key] = entry
                newcall = False
                line_index += 1
            elif line_string == "\n":
                n = 0
                key = "empty_line" + "_" + str(n)
                while key in group:
                    n += 1
                    key = "empty_line_" + str(n)
                group[key] = entry
                newcall = False
                line_index += 1
            else:
                key = entry.key
                n = 0
                while key in group:
                    n += 1
                    key = entry.key + "_" + str(n)
                group[key] = entry
                newcall = False
                line_index += 1

        return group, line_index

    @staticmethod
    def error_notification(e):
        print(e)
        print("Reading Error Notification")

    def outputString(self):
        return self["ROOT"].outputString()

    def checkSetup(self):
        simulation_task_manager = self["ROOT"]["DESIGN3D_COMPUTATION_0"][
            "DATABASE_GENERATION_MINAMO_0"
        ]["SIMULATION_TASK_MANAGER_0"]

        simulation_task_manager["MODEL_EXTENSION"].value = "prt"
        simulation_task_manager["CFD_GEOM_EXTENSION"].value = "stp"

        for idx, group in enumerate(
            (
                simulation_task_manager["SIMULATION_TASKS_0"][
                    "SIMULATION_TASK_PARAM_GEOM_MODEL_0"
                ],
                simulation_task_manager["SIMULATION_TASKS_0"][
                    "SIMULATION_TASK_IGG_AUTOGRID_0"
                ],
                simulation_task_manager["SIMULATION_TASKS_0"][
                    "SIMULATION_TASK_EURANUS_TURBO_0"
                ],
                simulation_task_manager["SIMULATION_TASKS_0"][
                    "SIMULATION_TASK_CFVIEW_0"
                ],
            )
        ):
            group["TASK_PROCESSING"].value = str(
                int(not (idx % 3))
            )  # Activate only n.0 and n.3
            group["CHAIN_TYPE"].value = "EXTERNAL"
            group["IMPORT_SCRIPTS"].value = "1"

    def setParamScript(self, script_name):
        self["ROOT"]["DESIGN3D_COMPUTATION_0"]["DATABASE_GENERATION_MINAMO_0"][
            "SIMULATION_TASK_MANAGER_0"
        ]["SIMULATION_TASKS_0"]["SIMULATION_TASK_PARAM_GEOM_MODEL_0"][
            "EXTERNAL_SCRIPT"
        ].value = (
            '"' + script_name + '"'
        )

    def setMeshScript(self, script_name):
        self["ROOT"]["DESIGN3D_COMPUTATION_0"]["DATABASE_GENERATION_MINAMO_0"][
            "SIMULATION_TASK_MANAGER_0"
        ]["SIMULATION_TASKS_0"]["SIMULATION_TASK_IGG_AUTOGRID_0"][
            "EXTERNAL_SCRIPT"
        ].value = (
            '"' + script_name + '"'
        )

    def setSolverScript(self, script_name):
        self["ROOT"]["DESIGN3D_COMPUTATION_0"]["DATABASE_GENERATION_MINAMO_0"][
            "SIMULATION_TASK_MANAGER_0"
        ]["SIMULATION_TASKS_0"]["SIMULATION_TASK_EURANUS_TURBO_0"][
            "EXTERNAL_SCRIPT"
        ].value = (
            '"' + script_name + '"'
        )

    def setPostProScript(self, script_name):
        self["ROOT"]["DESIGN3D_COMPUTATION_0"]["DATABASE_GENERATION_MINAMO_0"][
            "SIMULATION_TASK_MANAGER_0"
        ]["SIMULATION_TASKS_0"]["SIMULATION_TASK_CFVIEW_0"]["EXTERNAL_SCRIPT"].value = (
            '"' + script_name + '"'
        )

    def createPostProDefaultMacro(self):
        stringlist = []
        stringlist.append("                  NI_BEGIN\tUSER_DEFINED_MACRO\n")
        stringlist.append(
            "                     SOLUTION_FILE                                      3D\n"
        )
        stringlist.append(
            "                     MACRO_FILE                                         myPath/myScript.py\n"
        )
        stringlist.append(
            "                     DATA_FILE                                          myScript.dat\n"
        )
        stringlist.append(
            "                     QUANTITY_NAME                                      myQuantity\n"
        )
        stringlist.append(
            "                     DIM                                                SCALAR\n"
        )
        stringlist.append(
            "                     ACTIVE                                             1\n"
        )
        stringlist.append("                  NI_END\tUSER_DEFINED_MACRO\n")
        return self.deepTree(stringlist, 0)

    def createPostProMacro(self, script_name):
        new_post_pro_macro, _ = self.createPostProDefaultMacro()
        new_post_pro_macro["MACRO_FILE"].value = "macro_CFV/" + script_name
        new_post_pro_macro["DATA_FILE"].value = script_name.rsplit(".", 1)[0] + ".dat"
        new_post_pro_macro["QUANTITY_NAME"].value = script_name.rsplit(".", 1)[0]
        return new_post_pro_macro

    def addPostProMacro(self, script_name):
        postProMacroLayer = self["ROOT"]["DESIGN3D_COMPUTATION_0"][
            "DATABASE_GENERATION_MINAMO_0"
        ]["SIMULATION_TASK_MANAGER_0"]["SIMULATION_TASKS_0"][
            "SIMULATION_TASK_CFVIEW_0"
        ][
            "USER_DEFINED_MACROS_EXTERNAL_0"
        ]

        if isinstance(script_name, iecGroup):
            new_post_pro_macro = script_name
        elif isinstance(script_name, str):
            new_post_pro_macro = self.createPostProMacro(script_name)
        else:
            raise CustomError

        n = 0
        new_group_name = "USER_DEFINED_MACRO" + "_" + str(n)
        while new_group_name in postProMacroLayer:
            n += 1
            new_group_name = "USER_DEFINED_MACRO" + "_" + str(n)

        self["ROOT"]["DESIGN3D_COMPUTATION_0"]["DATABASE_GENERATION_MINAMO_0"][
            "SIMULATION_TASK_MANAGER_0"
        ]["SIMULATION_TASKS_0"]["SIMULATION_TASK_CFVIEW_0"][
            "USER_DEFINED_MACROS_EXTERNAL_0"
        ] = self.insert_key_value(
            postProMacroLayer,
            new_group_name,
            "NI_END_USER_DEFINED_MACROS_EXTERNAL",
            new_post_pro_macro,
        )

    def removePostProMacro(self, number=None):
        post_pro_macro_layer = self["ROOT"]["DESIGN3D_COMPUTATION_0"][
            "DATABASE_GENERATION_MINAMO_0"
        ]["SIMULATION_TASK_MANAGER_0"]["SIMULATION_TASKS_0"][
            "SIMULATION_TASK_CFVIEW_0"
        ][
            "USER_DEFINED_MACROS_EXTERNAL_0"
        ]

        if number is None:
            n = 0
            last_group_name = "USER_DEFINED_MACRO" + "_" + str(n)
            while last_group_name in post_pro_macro_layer:
                n += 1
                last_group_name = "USER_DEFINED_MACRO" + "_" + str(n)
            n -= 1
            last_group_name = "USER_DEFINED_MACRO" + "_" + str(n)

        elif isinstance(number, int):
            last_group_name = "USER_DEFINED_MACRO" + "_" + str(number)

        else:
            raise CustomError

        self["ROOT"]["DESIGN3D_COMPUTATION_0"]["DATABASE_GENERATION_MINAMO_0"][
            "SIMULATION_TASK_MANAGER_0"
        ]["SIMULATION_TASKS_0"]["SIMULATION_TASK_CFVIEW_0"][
            "USER_DEFINED_MACROS_EXTERNAL_0"
        ].pop(
            last_group_name
        )

    def exportNpyArray(self, row_number=0, blade_number=0):
        ni_blade_geometry = self.retrieveNiBladeGeometry(row_number, blade_number)

        suction = []
        pressure = []
        for item in ni_blade_geometry.suctionList:
            section = np.vstack(
                [item.X, item.Y, item.Z, np.zeros(item.numberOfPointsInt)]
            ).transpose()
            suction.append(section)
        for item in ni_blade_geometry.pressureList:
            section = np.vstack(
                [item.X, item.Y, item.Z, np.ones(item.numberOfPointsInt)]
            ).transpose()
            section = np.flip(section, axis=0)
            pressure.append(section)
        return np.array([(np.asarray(suction), np.asarray(pressure))], dtype=float)

    def exportNpyArrayCyl(self, row_number=0, blade_number=0):
        ni_blade_geometry = self.retrieveNiBladeGeometry(row_number, blade_number)
        if not self.cylCoordDefined(row_number, blade_number):
            self.convertCartesian2Cyl(row_number, blade_number)
        suction = []
        pressure = []
        for item in ni_blade_geometry.suctionList:
            section = np.vstack(
                [item.R, item.THETA, item.Z, np.zeros(item.numberOfPointsInt)]
            ).transpose()
            suction.append(section)
        for item in ni_blade_geometry.pressureList:
            section = np.vstack(
                [item.R, item.THETA, item.Z, np.ones(item.numberOfPointsInt)]
            ).transpose()
            section = np.flip(section, axis=0)
            pressure.append(section)
        return np.array([(np.asarray(suction), np.asarray(pressure))], dtype=float)

    def convertCartesian2Cyl(self, row_number=0, blade_number=0):
        ni_blade_geometry = self.retrieveNiBladeGeometry(row_number, blade_number)
        for item in ni_blade_geometry.suctionList:
            item.R = []
            item.THETA = []
            for index in range(len(item.X)):
                item.R.append(np.hypot(item.Y[index], item.X[index]))
                item.THETA.append(np.arctan2(item.Y[index], item.X[index]))
        for item in ni_blade_geometry.pressureList:
            item.R = []
            item.THETA = []
            for index in range(len(item.X)):
                item.R.append(np.hypot(item.Y[index], item.X[index]))
                item.THETA.append(np.arctan2(item.Y[index], item.X[index]))

    def cylCoordDefined(self, row_number=0, blade_number=0):
        ni_blade_geometry = self.retrieveNiBladeGeometry(row_number, blade_number)
        check = 0
        for item in ni_blade_geometry.suctionList:
            check += len(item.THETA) + len(item.R)
        for item in ni_blade_geometry.pressureList:
            check += len(item.THETA) + len(item.R)
        return bool(check)

    def importNpyArrayCyl(self, array, row_number=0, blade_number=0):
        # array shape (2,nSections,nPoints,4)
        ni_blade_geometry = self.retrieveNiBladeGeometry(row_number, blade_number)
        n_sections_from_array = array.shape[1]
        ni_blade_geometry.setNumberOfSections(n_sections_from_array)
        for idx, suction in enumerate(ni_blade_geometry.suctionList):
            new_list = array[0][idx].transpose().tolist()
            suction.updateArraysCyl(new_list[0], new_list[1], new_list[2])
        for idx, pressure in enumerate(ni_blade_geometry.pressureList):
            new_list = array[1][idx].transpose().tolist()
            pressure.updateArraysCyl(
                new_list[0][::-1], new_list[1][::-1], new_list[2][::-1]
            )

    def importNpyArray(self, array, row_number=0, blade_number=0):
        # array shape (2,nSections,nPoints,4)
        ni_blade_geometry = self.retrieveNiBladeGeometry(row_number, blade_number)
        n_sections_from_array = array.shape[1]
        ni_blade_geometry.setNumberOfSections(n_sections_from_array)
        for idx, suction in enumerate(ni_blade_geometry.suctionList):
            new_list = array[0][idx].transpose().tolist()
            suction.updateArrays(new_list[0], new_list[1], new_list[2])
        for idx, pressure in enumerate(ni_blade_geometry.pressureList):
            new_list = array[1][idx].transpose().tolist()
            pressure.updateArrays(
                new_list[0][::-1], new_list[1][::-1], new_list[2][::-1]
            )

    def retrieveNiBladeGeometry(self, row_number=0, blade_number=0):
        row_occurence = -1
        blade_occurence = -1
        blade_key = ""

        row_key = self.retrieve_row_key(row_number)

        for key in self["ROOT"]["GEOMTURBO"][row_key].keys():
            if "NIBlade" in key or "NIBLADE" in key:
                blade_occurence += 1
                if blade_occurence == blade_number:
                    blade_key = key

        if row_key == "":
            print("Row not defined")
        if blade_key == "":
            print("Blade not defined")

        if "NIROW" in row_key:
            ni_blade_geometry = self["ROOT"]["GEOMTURBO"][row_key][blade_key][
                "NIBLADEGEOMETRY_0"
            ]
        elif "nirow" in row_key:
            ni_blade_geometry = self["ROOT"]["GEOMTURBO"][row_key][blade_key][
                "nibladegeometry_0"
            ]
        else:
            print("ERROR")

        return ni_blade_geometry

    def set_row_periodicity(self, periodicity, rowNumber=0):
        row_key = self.retrieve_row_key(rowNumber)

        if row_key == "" or row_key == None:
            print("Row not defined")
        else:
            self["ROOT"]["GEOMTURBO"][row_key]["PERIODICITY"].value = str(periodicity)

    def get_row_periodicity(self, rowNumber=0):
        row_key = self.retrieve_row_key(rowNumber)
        if row_key == "" or row_key == None:
            print("Row not defined")
        else:
            return self["ROOT"]["GEOMTURBO"][row_key]["PERIODICITY"].value

    def set_row_speed(self, row_speed, rowNumber=0):
        row_key = self.retrieve_row_key(rowNumber)

        if row_key == "" or row_key == None:
            print("Row not defined")
        else:
            try:
                self["ROOT"]["GEOMTURBO"][row_key]["ROTATION_SPEED"].value = str(
                    row_speed
                )
            except:
                rot_speed = iecEntry()
                rot_speed.key = "ROTATION_SPEED"
                rot_speed.value = str(row_speed)
                rot_speed.leadingSpaceString = self["ROOT"]["GEOMTURBO"][row_key][
                    "PERIODICITY"
                ].leadingSpaceString
                rot_speed.keyTagSpaceString = self["ROOT"]["GEOMTURBO"][row_key][
                    "PERIODICITY"
                ].keyTagSpaceString
                rot_speed.tagValueSpaceString = self["ROOT"]["GEOMTURBO"][row_key][
                    "PERIODICITY"
                ].tagValueSpaceString
                rot_speed.trailingSpaceString = self["ROOT"]["GEOMTURBO"][row_key][
                    "PERIODICITY"
                ].trailingSpaceString
                last_item_key = list(self["ROOT"]["GEOMTURBO"][row_key].keys())[-1]
                last_item_copy = deepcopy(
                    self["ROOT"]["GEOMTURBO"][row_key][last_item_key]
                )
                del self["ROOT"]["GEOMTURBO"][row_key][last_item_key]
                self["ROOT"]["GEOMTURBO"][row_key]["ROTATION_SPEED"] = rot_speed
                self["ROOT"]["GEOMTURBO"][row_key][last_item_key] = last_item_copy

    def get_row_speed(self, rowNumber=0):
        row_key = self.retrieve_row_key(rowNumber)
        if row_key == "" or row_key == None:
            print("Row not defined")
        else:
            try:
                row_speed = self["ROOT"]["GEOMTURBO"][row_key]["ROTATION_SPEED"].value
                return row_speed
            except:
                return "NaN"

    def retrieve_row_key(self, rowNumber):
        row_occurence = -1
        for key in self["ROOT"]["GEOMTURBO"].keys():
            if "nirow" in key or "NIROW" in key:
                row_occurence += 1
                if row_occurence == rowNumber:
                    return key
        return None

    def merge_ZR(self):
        if "GEOMTURBO" not in self["ROOT"].keys():
            return
        basic_curve_dict = self.get_basic_curve_dict()
        hub_vertex_list = self.get_vertex_list("channel_curve_hub_0")
        shroud_vertex_list = self.get_vertex_list("channel_curve_shroud_0")

        self.append_and_update_curves(basic_curve_dict, hub_vertex_list)
        self.append_and_update_curves(basic_curve_dict, shroud_vertex_list)

    def get_vertex_list(self, channel_name):
        vertex_list = []
        for key in self["ROOT"]["GEOMTURBO"]["CHANNEL_0"][channel_name].keys():
            if "VERTEX" in key:
                vertex_list.append(
                    (
                        channel_name,
                        key,
                        self["ROOT"]["GEOMTURBO"]["CHANNEL_0"][channel_name][key].value[
                            0
                        ],
                    )
                )
        return vertex_list

    def get_basic_curve_dict(self):
        basic_curve_dict = {}
        for key in self["ROOT"]["GEOMTURBO"]["CHANNEL_0"].keys():
            if "basic_curve" in key:
                try:
                    name = self["ROOT"]["GEOMTURBO"]["CHANNEL_0"][key]["NAME"].value
                    zrList = self["ROOT"]["GEOMTURBO"]["CHANNEL_0"][key]["zrcurve_0"]
                    basic_curve_dict[name] = (key, zrList)
                except:
                    pass
        return basic_curve_dict

    def append_and_update_curves(self, basic_curve_dict, vertex_list):
        for item in basic_curve_dict.items():
            curve = item[1][1]
            if curve.numberOfPoints == 2:
                # QUI bisogna aggiungere i punti
                # pass
                curve.uniformIncreasePointsNumber(50)

        base_curve = vertex_list[1][2]
        for curve in vertex_list[2:]:
            basic_curve_dict[base_curve][1].append(basic_curve_dict[curve[2]][1])
            key_to_remove = basic_curve_dict[curve[2]][0]
            del self["ROOT"]["GEOMTURBO"]["CHANNEL_0"][key_to_remove]
            del self["ROOT"]["GEOMTURBO"]["CHANNEL_0"][curve[0]][curve[1]]

    def extractChannelCurves(self, channel_curve_name):
        basic_curve_dict = self.get_basic_curve_dict()
        # channel_curve_name possible values = channel_curve_hub_0
        #                                      channel_curve_shroud_0
        if "shroud" in channel_curve_name:
            zeros_or_ones = np.ones
        elif "hub" in channel_curve_name:
            zeros_or_ones = np.zeros
        else:
            raise Exception("ERROR ZERO ONE HUB SHROUD")

        curve_array_list = []
        avoid_first_occurrence = True
        for key, item in self["ROOT"]["GEOMTURBO"]["CHANNEL_0"][
            channel_curve_name
        ].items():
            if "VERTEX" in key:
                if not avoid_first_occurrence:
                    curve_name = item.value[0]
                    curve = basic_curve_dict[curve_name][1]
                    curve_array = np.vstack(
                        [
                            np.zeros(curve.numberOfPoints),
                            curve.R,
                            curve.Z,
                            zeros_or_ones(curve.numberOfPoints),
                        ]
                    ).transpose()
                    curve_array = np.expand_dims(curve_array, axis=0)
                    curve_array_list.append(curve_array)
                else:
                    avoid_first_occurrence = False
        return curve_array_list

    def exportZRNpyArraysList(self):
        hub_array_list = self.extractChannelCurves("channel_curve_hub_0")
        shroud_array_list = self.extractChannelCurves("channel_curve_shroud_0")
        return (hub_array_list, shroud_array_list)

    def vStackArray(self, arrayList):
        if arrayList[0].shape[1] == 2:
            vStackArray = self.fillZRArray(arrayList[0], 50)
        else:
            vStackArray = arrayList[0]
        for array in arrayList[1:]:
            if array.shape[1] == 2:
                array = self.fillZRArray(array, 50)
            vStackArray = np.append(vStackArray, array[:, 1:, :], axis=1)
        return vStackArray

    def fillZRArray(self, array, nPoints):
        if array[0, 0, 3] == 0:
            zeros_or_ones = np.zeros
        elif array[0, 0, 3] == 1:
            zeros_or_ones = np.ones
        else:
            raise Exception("ERROR ZERO ONE HUB SHROUD")
        ref = np.array([0, 1])
        X = np.linspace(0, 1, num=nPoints)
        R = np.interp(X, ref, array[0, :, 1])
        Z = np.interp(X, ref, array[0, :, 2])
        newArray = np.vstack(
            [np.zeros(nPoints), R, Z, zeros_or_ones(nPoints)]
        ).transpose()
        return np.expand_dims(newArray, axis=0)

    def exportZRNpyArrays(self):
        hub_array_list, shroud_array_list = self.exportZRNpyArraysList()
        return (self.vStackArray(hub_array_list), self.vStackArray(shroud_array_list))

    def importZRNpyArrays(self, hub_section, shroud_section):
        self.importZRNpyHubArray(hub_section)
        self.importZRNpyShroudArray(shroud_section)
        pass

    def importZRNpyHubArray(self, hub_section):
        self.importZRNpyGenericArrayWithKey(hub_section, "channel_curve_hub_0")
        pass

    def importZRNpyShroudArray(self, shroud_section):
        self.importZRNpyGenericArrayWithKey(shroud_section, "channel_curve_shroud_0")
        pass

    def importZRNpyGenericArrayWithKey(self, section, key):
        basic_curve_dict = self.get_basic_curve_dict()
        curve_name = self["ROOT"]["GEOMTURBO"]["CHANNEL_0"][key]["VERTEX"].value[0]
        curve = basic_curve_dict[curve_name][1]
        curve.updateArrays(section[:, 2], section[:, 1])
        curve.numberOfPoints = section.shape[0]

    def importZRNpyArray(self, section):
        if np.all(section[0, :, 3] == 0):
            self.setNumberOfBasicCurvesHub(1)
            self.importZRNpyHubArray(section[0])
        elif np.all(section[0, :, 3] == 1):
            self.setNumberOfBasicCurvesShroud(1)
            self.importZRNpyShroudArray(section[0])
        else:
            raise Exception("ERROR: NON COHERENT ARRAY")

    def importZRNpyArrayList(self, sections_list):
        if np.all(sections_list[0][0, :, 3] == 0):
            # Hub section
            self.setNumberOfBasicCurvesHub(len(sections_list))
            self.updateGenericSectionsFromList(sections_list, "channel_curve_hub_0")
        elif np.all(sections_list[0][0, :, 3] == 1):
            # Shroud section
            self.setNumberOfBasicCurvesShroud(len(sections_list))
            self.updateGenericSectionsFromList(sections_list, "channel_curve_shroud_0")

    def updateGenericSectionsFromList(self, section_list, hub_or_shroud):
        names_of_basic_curve_list = self.getNamesListOfBasicCurvesGeneric(hub_or_shroud)
        if len(names_of_basic_curve_list) != len(section_list):
            raise Exception("ERROR: mismatch between endwalls sections number")

        for idx, curve_name in enumerate(names_of_basic_curve_list):
            basic_curve_dict = self.get_basic_curve_dict()
            curve = basic_curve_dict[curve_name][1]
            curve.updateArrays(section_list[idx][0, :, 2], section_list[idx][0, :, 1])
            curve.numberOfPoints = section_list[idx].shape[1]

    def importZRNpyArray2(self, section):
        if isinstance(section, list) and isinstance(section[0], np.ndarray):
            # Sections divided in list
            self.importZRNpyArrayList(section)
            pass
        elif isinstance(section, np.ndarray):
            # Single section
            self.importZRNpyArray(section)
        else:
            raise Exception("ERROR: wrong format of endwalls ")

    def getNumberOfBasicCurvesHub(self):
        return len(self.getNamesListOfBasicCurvesHub())

    def getNumberOfBasicCurvesShroud(self):
        return len(self.getNamesListOfBasicCurvesShroud())

    def getNamesListOfBasicCurvesHub(self):
        return self.getNamesListOfBasicCurvesGeneric("channel_curve_hub_0")

    def getNamesListOfBasicCurvesShroud(self):
        return self.getNamesListOfBasicCurvesGeneric("channel_curve_shroud_0")

    def getNamesListOfBasicCurvesGeneric(self, hub_or_shroud):
        vertex_list = self["ROOT"]["GEOMTURBO"]["CHANNEL_0"][hub_or_shroud]
        vertex_number = -1  # Because the first one is always used twice
        names_list_of_basic_curves = []
        for key, item in vertex_list.items():
            if "VERTEX" in key:
                vertex_number += 1
                names_list_of_basic_curves.append(item.value[0])
        del names_list_of_basic_curves[0]
        return names_list_of_basic_curves

    def setNumberOfBasicCurvesHub(self, number):
        return self.setNumberOfBasicCurvesGeneric(number, "channel_curve_hub_0")
        pass

    def setNumberOfBasicCurvesShroud(self, number):
        return self.setNumberOfBasicCurvesGeneric(number, "channel_curve_shroud_0")
        pass

    def setNumberOfBasicCurvesGeneric(self, number, hub_or_shroud):
        basic_curve_dict = self.get_basic_curve_dict()
        names_list = self.getNamesListOfBasicCurvesGeneric(hub_or_shroud)
        if number < len(names_list):
            for i in range(len(names_list) - number):
                self.removeLastBasicCurveGeneric(hub_or_shroud)
        elif number > len(names_list):
            for i in range(number - len(names_list)):
                self.addBasicCurveGeneric(hub_or_shroud)

    def removeLastBasicCurveHub(self):
        return self.removeLastBasicCurveGeneric("channel_curve_hub_0")

    def removeLastBasicCurveShroud(self):
        return self.removeLastBasicCurveGeneric("channel_curve_shroud_0")

    def removeLastBasicCurveGeneric(self, hub_or_shroud):
        names_of_basic_curve_list = self.getNamesListOfBasicCurvesGeneric(hub_or_shroud)
        if len(names_of_basic_curve_list) <= 1:
            raise Exception("Minimum basic curve number already reached")
        basic_curve_dict = self.get_basic_curve_dict()
        vertex_list = self["ROOT"]["GEOMTURBO"]["CHANNEL_0"][hub_or_shroud]
        last_item_name = names_of_basic_curve_list[-1]
        for key, item in vertex_list.items():
            if item.value[0] == last_item_name:
                del vertex_list[key]
                break
        basic_curve_name_to_be_removed = basic_curve_dict[last_item_name][0]
        del self["ROOT"]["GEOMTURBO"]["CHANNEL_0"][basic_curve_name_to_be_removed]

    def addBasicCurveItem(self, new_item_name, new_curve_name):
        main_channel = self["ROOT"]["GEOMTURBO"]["CHANNEL_0"]
        first_item_key = next(iter(main_channel))

        for key, item in main_channel.items():
            if "basic_curve" in key:
                try:
                    zrList = self["ROOT"]["GEOMTURBO"]["CHANNEL_0"][key]["zrcurve_0"]
                    first_basic_curve = item
                    break
                except:
                    pass

        main_channel[new_item_name] = deepcopy(first_basic_curve)
        main_channel.move_to_end(new_item_name, False)
        main_channel.move_to_end(first_item_key, False)
        main_channel[new_item_name]["NAME"].value = new_curve_name

    def addBasicCurveHub(self):
        return self.addBasicCurveGeneric("channel_curve_hub_0")

    def addBasicCurveShroud(self):
        return self.addBasicCurveGeneric("channel_curve_shroud_0")

    def cleanUnusedBasicCurves(self):
        names_of_used_basic_curve_list = (
            self.getNamesListOfBasicCurvesHub() + self.getNamesListOfBasicCurvesShroud()
        )
        main_channel = self["ROOT"]["GEOMTURBO"]["CHANNEL_0"]
        list_of_keys_to_be_removed = []
        for key, item in main_channel.items():
            if (
                "basic_curve" in key
                and item["NAME"].value not in names_of_used_basic_curve_list
            ):
                list_of_keys_to_be_removed.append(key)

        for key in list_of_keys_to_be_removed:
            del main_channel[key]

    def addBasicCurveGeneric(self, hub_or_shroud):
        names_of_basic_curve_list = (
            self.getNamesListOfBasicCurvesHub() + self.getNamesListOfBasicCurvesShroud()
        )
        vertex_list = self["ROOT"]["GEOMTURBO"]["CHANNEL_0"][hub_or_shroud]
        last_curve_name = names_of_basic_curve_list[-1]
        last_vertex_name = list(vertex_list.keys())[-2]
        last_item_name = list(vertex_list.keys())[-1]
        last_number = re.search(r"\d+$", last_curve_name)

        if last_number:
            residual = re.search(r".+?(?=\d+$)", last_curve_name).group(0)
            last_number = int(last_number.group(0))
        else:
            residual = last_curve_name
            last_number = 0
        free_name_found = True
        counter = 0
        while free_name_found:
            counter += 1
            new_curve_name = residual + str(last_number + counter)
            free_name_found = new_curve_name in names_of_basic_curve_list
        free_vertex_key_found = True
        counter = 0
        while free_vertex_key_found:
            counter += 1
            new_vertex_key = "VERTEX_" + str(counter)
            free_vertex_key_found = new_vertex_key in vertex_list.keys()

        new_item = iecEntry(vertex_list[last_vertex_name])
        new_item.value = [new_curve_name, str(1)]
        vertex_list[new_vertex_key] = new_item
        vertex_list.move_to_end(last_item_name)

        basic_curve_dict = self.get_basic_curve_dict()

        free_name_found = True
        counter = 0
        while free_name_found:
            counter += 1
            new_item_name = "basic_curve_" + str(counter)
            free_name_found = {
                k: v for k, v in basic_curve_dict.items() if v[0] == new_item_name
            }

        self.addBasicCurveItem(new_item_name, new_curve_name)
        pass


class CustomError(Exception):
    pass
