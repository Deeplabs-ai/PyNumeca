"""Test reading a geomturbo file
"""

import logging
import os

from pynumeca.reader.numecaParser import numecaParser


def test_reading_geomturbo():
    """Test reading a geomturbo file"""
    test = []
    test.append(numecaParser())
    test.append(numecaParser())
    test.append(numecaParser())
    test.append(numecaParser())
    test[0].load("tests/data/C2_rev4.geomTurbo")
    test[1].load("tests/data/Rotor37_Autoblade.geomTurbo")
    test[2].load("tests/data/template_rotor_g_v4.geomTurbo")
    test[3].load("tests/data/C2_Mappe_DB_51_r2_final.geomTurbo")

    for i, item in enumerate(test):
        # Test row periodicity reading and writing
        blade_count = item.get_row_periodicity(0)
        print("Before = ", blade_count)
        item.set_row_periodicity(int(blade_count) + 2, 0)
        blade_count = item.get_row_periodicity(0)
        print("After = ", blade_count)

        # Test row speed reading and writing
        bladespeed = item.get_row_speed(0)
        print("Before = ", bladespeed)
        if bladespeed == "NaN":
            bladespeed = 1234
        item.set_row_speed(float(bladespeed) + 1000, 0)
        bladespeed = item.get_row_speed(0)
        print("After = ", bladespeed)

        # Test export array for blades with cartesian coordinates
        output = item.exportNpyArray()
        logging.info(output.shape)
        item.importNpyArray(output[0])

        # Test export array for blades with cylindrical coordinates
        output = item.exportNpyArrayCyl()
        logging.info(output.shape)
        item.importNpyArrayCyl(output[0])

        # Test export array for hub and shroud
        out_hub, out_shroud = item.exportZRNpyArrays()
        logging.info(out_hub.shape, out_shroud.shape)

        # Test import array for hub and shroud
        # item.importZRNpyArray(outHub[0])
        # item.importZRNpyArray(outShroud[0])

        # Test export array for hub and shroud as list of segments
        out_hub_list, out_shroud_list = item.exportZRNpyArraysList()
        logging.info(len(out_hub_list), len(out_shroud_list))

        # Test import of list of arrays for hub and shroud
        item.importZRNpyArray2(out_hub_list)
        item.importZRNpyArray2(out_shroud_list)

        with open(f"test_file_{i}.txt", "w", encoding="utf-8") as output_file:
            output_file.write(item.outputString())

    for file in os.listdir():
        if "test_file" in file:
            os.remove(file)
