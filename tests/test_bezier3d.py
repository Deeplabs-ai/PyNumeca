"""
Test Bezier3D compressor
"""

import os

from PyNumeca.preprocessing.bezier_geomturbo import BezierCompressor


def test_bezier3d_compressor():
    """Test Bezier3D compressor"""
    samples = [
        "tests/data/C2_rev4.geomTurbo",
        "tests/data/C2_Mappe_DB_51_r2_final.geomTurbo",
    ]

    for sample in samples:
        bezier_compressor = BezierCompressor(
            sample,
            bezier_degree=[[9, 7, 9], [9, 7, 9], [9, 7, 9, 7]],
            is_blunt_te=[True, True, False],
            evaluation_points=[[100, 50, 100], [100, 50, 100], [100, 50, 100, 50]],
            split_edges=[False, False, False],
            is_main_blade_active=True,
            is_splitter_active=True,
            is_diffuser_active=True,
        )
        bezier_compressor.load_compressor_from_file()
        bezier_compressor.fit_compressor_with_bezier()
        bezier_compressor.set_control_points(
            "main_blade", bezier_compressor.main_blade.control_points
        )
        bezier_compressor.get_compressor_from_control_points()

        bezier_compressor.save(path="trial.bin")
        new_bc = BezierCompressor.load("trial.bin")
        new_bc.main_blade.draw_blade(show=False)
        os.remove("trial.bin")
