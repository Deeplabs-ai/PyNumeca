from PyNumeca.reader.numecaParser import numecaParser
import os

def test_reading_geomTurbo():
    ciao = numecaParser()
    ciao2 = numecaParser()
    ciao3 = numecaParser()
    ciao.load("tests/C2_rev4.geomTurbo")
    ciao2.load("tests/Rotor37_Autoblade.geomTurbo")
    ciao3.load("tests/template_rotor_g_v4.geomTurbo")

    output = ciao.exportNpyArray()
    print(output.shape)

    output = ciao2.exportNpyArray()
    print(output.shape)

    output = ciao3.exportNpyArray()
    print(output.shape)




    with open("tests/demofile1.txt", "w") as f:
        f.write(ciao.outputString())
    with open("tests/demofile2.txt", "w") as f:
        f.write(ciao2.outputString())
    with open("tests/demofile3.txt", "w") as f:
        f.write(ciao3.outputString())


if __name__=="__main__":
    os.chdir(os.path.dirname(os.getcwd()))
    test_reading_geomTurbo()