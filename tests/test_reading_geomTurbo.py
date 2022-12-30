import logging
import os

import numpy as np

from PyNumeca.reader.numecaParser import numecaParser


def test_reading_geomturbo():
    test = []
    test.append(numecaParser())
    test.append(numecaParser())
    test.append(numecaParser())
    test.append(numecaParser())
    test[0].load("data/C2_rev4.geomTurbo")
    test[1].load("data/Rotor37_Autoblade.geomTurbo")
    test[2].load("data/template_rotor_g_v4.geomTurbo")
    test[3].load("data/C2_Mappe_DB_51_r2_final.geomTurbo")

    for i, item in enumerate(test):
        # Test row periodicity reading and writing
        bladeCount = item.get_row_periodicity(0)
        print("Before = ", bladeCount)
        item.set_row_periodicity(int(bladeCount) + 2, 0)
        bladeCount = item.get_row_periodicity(0)
        print("After = ", bladeCount)

        # Test row speed reading and writing
        bladespeed = item.get_row_speed(0)
        print("Before = ", bladespeed)
        if (bladespeed == "NaN"): bladespeed = 1234
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

        with open(f"test_file_{i}.txt", "w") as f:
            f.write(item.outputString())

    for file in os.listdir():
        if 'test_file' in file:
            os.remove(file)
            pass
