def generate_mesh_script(filename: str,
                         default_trb_path: str,
                         geomturbo_path: str,
                         export_path: str):
    code = \
        """
a5_open_project("@default_trb_path")
a5_import_and_replace_geometry_file("@geomturbo_path")
a5_generate_3d()
a5_save_project("@export_path")
""".replace('@default_trb_path', default_trb_path).replace('@geomturbo_path', geomturbo_path).replace(
            '@export_path', export_path)

    with open(filename, 'w') as f:
        f.write(code)


