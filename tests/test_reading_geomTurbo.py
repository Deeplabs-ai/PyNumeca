import logging
import os

from PyNumeca.reader.numecaParser import numecaParser


def test_reading_geomturbo():
    test = numecaParser()
    test_2 = numecaParser()
    test_3 = numecaParser()
    test.load("data/C2_rev4.geomTurbo")
    test_2.load("data/Rotor37_Autoblade.geomTurbo")
    test_3.load("data/template_rotor_g_v4.geomTurbo")


    for i, item in enumerate([test, test_2, test_3]):
        # Test row periodicity reading and writing
        bladeCount = item.get_row_periodicity(0)
        print("Before = ", bladeCount)
        item.set_row_periodicity(int(bladeCount) + 2, 0)
        bladeCount = item.get_row_periodicity(0)
        print("After = ", bladeCount)

        # Test export array
        output = item.exportNpyArray()
        logging.info(output.shape)
        item.importNpyArray(output[0])

        with open(f"test_file_{i}.txt", "w") as f:
            f.write(test.outputString())

    for file in os.listdir():
        if 'test_file' in file:
            os.remove(file)

