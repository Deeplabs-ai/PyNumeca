def generate_fine_script(filename: str,
                         default_iec_path: str,
                         trb_path: str,
                         export_path: str,
                         duplicate_results: bool = 0):
    code = \
        """
open_project("@default_iec_path")
link_mesh_file("@trb_path", 1)
save_project_as("@export_path", @duplicate_results)
""".replace('@default_iec_path', default_iec_path).replace('@trb_path', trb_path).replace(
            '@export_path', export_path).replace('@duplicate_results', str(duplicate_results))

    with open(filename, 'w') as f:
        f.write(code)
