import os

from PyNumeca.constants import constants


def run_fine_script(path: str, ui: bool = False):
    if not os.path.exists(path):
        raise FileNotFoundError('Cannot find {0}'.format(path))

    command = 'fine{0} '.format(constants.version)
    if not ui:
        command += '-batch '

    command += '-script {0}'.format(path)

    os.system(command)