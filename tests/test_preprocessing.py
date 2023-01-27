import os

from PyNumeca.preprocessing import turbo
from pyfluids import FluidsList


def test_centrifugal_compressor():
    geomturbo = 'data/C2_rev4.geomTurbo'
    mf = 'data/example.mf'

    compressor = turbo.CentrifugalCompressor(fluid=FluidsList.Air)
    compressor.load_geometry_from_geometurbo(geomturbo)
    compressor.load_boundaries_and_performances_from_mf(mf)

    compressor.save('tmp.bin')
    new_compressor = turbo.CentrifugalCompressor.load('tmp.bin')
    os.remove('tmp.bin')

