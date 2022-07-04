import os

from PyNumeca.constants import constants


def run_igg_script(path: str, ui: bool = False):
    if not os.path.exists(path):
        raise FileNotFoundError('Cannot find {0}'.format(path))

    command = 'igg{0} -autogrid5 '.format(constants.version)
    if not ui:
        command += '-batch '

    command += '-script {0} -debug'.format(path)

    os.system(command)
