import os
import shutil

import tqdm


def collect_design_3d_results(root_path: str, target_path: str, reset: bool = False):
    if reset:
        if os.path.exists(target_path):
            shutil.rmtree(target_path)

    if not os.path.exists(target_path):
        os.mkdir(target_path)

    target_geoms_path = os.path.join(target_path, "geometries")
    os.mkdir(target_geoms_path)

    target_performance_path = os.path.join(target_path, "performance")
    os.mkdir(target_performance_path)

    flow_files = []
    for file in os.listdir(root_path):
        if "flow" in file or "design" in file:
            if os.path.isdir(os.path.join(root_path, file)):
                flow_files.append(os.path.join(root_path, file))

    if len(flow_files) == 0:
        return ValueError("No flow/design files found")

    for file in tqdm.tqdm(flow_files):
        mesh_path = os.path.join(file, "_mesh")

        if not os.path.exists(mesh_path):
            continue

        for item in os.listdir(mesh_path):
            if "geomturbo" in item.lower():
                geom_path = os.path.join(mesh_path, item)
                break

        shutil.copy(
            src=geom_path,
            dst=os.path.join(
                target_geoms_path,
                os.path.basename(file)
                + os.path.splitext(os.path.basename(geom_path))[1],
            ),
        )

        perf_path = os.path.join(target_performance_path, os.path.basename(file))
        os.mkdir(perf_path)

        simulations_path = []
        for f in os.listdir(file):
            if os.path.isdir(os.path.join(file, f)):
                _path = os.path.join(file, f)
                _path_content = os.listdir(_path)
                for c in _path_content:
                    if (
                        os.path.splitext(c)[1] == ".res"
                        or os.path.splitext(c)[1] == ".mf"
                    ):
                        simulations_path.append(_path)
                        break

        for sim_path in simulations_path:
            for f in os.listdir(sim_path):
                if os.path.splitext(f)[1] == ".res" or os.path.splitext(f)[1] == ".mf":
                    shutil.copy(
                        src=os.path.join(sim_path, f), dst=os.path.join(perf_path, f)
                    )
