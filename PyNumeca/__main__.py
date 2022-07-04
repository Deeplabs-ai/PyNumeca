from PyNumeca.igg.utils import run_igg_script
import os


def main():
    run_igg_script(ui=True, path=os.path.join(os.getcwd(), 'sample_script.py'))
