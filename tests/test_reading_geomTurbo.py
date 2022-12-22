import logging
import os

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
        outHub, outShroud = item.exportZRNpyArrays()
        logging.info(outHub.shape, outShroud.shape)

        # Test import array for hub and shroud
        item.importZRNpyArray(outHub[0])
        item.importZRNpyArray(outShroud[0])

        # Test export array for hub and shroud as list of segments
        outHubList, outShroudList = item.exportZRNpyArraysList()
        logging.info(len(outHubList), len(outShroudList))

        with open(f"test_file_{i}.txt", "w") as f:
            f.write(item.outputString())

    for file in os.listdir():
        if 'test_file' in file:
            os.remove(file)
            pass
