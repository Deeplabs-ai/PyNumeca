"""
Test the preprocessing module.
"""

import os

from pyfluids import FluidsList  # type: ignore

from PyNumeca.preprocessing import turbo


def test_centrifugal_compressor():
    """Test centrifugal compressor loading and saving"""
    geomturbo = "tests/data/C2_rev4.geomTurbo"
    performance = "tests/data/example.mf"

    compressor = turbo.CentrifugalCompressor(fluid=FluidsList.Air)
    compressor.load_geometry_from_geomturbo(geomturbo)
    compressor.load_boundaries_and_performances_from_mf(performance)

    compressor.save("tmp.bin")
    turbo.CentrifugalCompressor.load("tmp.bin")
    os.remove("tmp.bin")
