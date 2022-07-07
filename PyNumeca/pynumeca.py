import os.path

from PyNumeca.fine import fine
from PyNumeca.igg import igg


class Simulation(object):
    def __init__(self,
                 name: str = 'Simulation',
                 working_path: str = None,
                 geomturbo_path: str = None,
                 iec_path: str = None,
                 trb_path: str = None):

        if working_path is not None:
            self.working_path = working_path
        if geomturbo_path is not None:
            self.geomturbo_path = geomturbo_path
        if iec_path is not None:
            self.iec_path = iec_path
        if trb_path is not None:
            self.trb_path = trb_path

        self.name = name

    def make_mesh(self):
        igg.a5_mesh_from_geomturbo(
            self.trb_path,
            self.geomturbo_path,
            # new_trb,
            os.path.join(self.working_path, self.name, self.name+'.igg'))

    def generate_run(self, index: int = 0):
        fine.fine_run_from_mesh(self.iec_path,
                                os.path.join(self.working_path, self.name, self.name+'.igg'),
                                os.path.join(self.working_path, self.name, self.name+'.iec'),
                                index=index)

    @staticmethod
    def setup_parallel_computation(run_file_path: str, cores: int = 20):
        fine.setup_parallel_computation(run_file_path, cores=cores)

    def run_pipeline(self, cores: int = 20, index: int = 0):
        self.make_mesh()
        self.generate_run(index)
        all_subdirs = [os.path.join(self.working_path, self.name, d) for d in os.listdir(os.path.join(self.working_path,
                                                                                                      self.name)) if
                       os.path.isdir(os.path.join(self.working_path, self.name, d))]
        all_runfiles = []
        for d in all_subdirs:
            for f in os.listdir(d):
                if os.path.isfile(os.path.join(d, f)) and ".run" in f:
                    all_runfiles.append(os.path.join(d, f))

        # print(all_runfiles)
        latest_runfile = str(max(all_runfiles, key=os.path.getmtime))
        print('Latest run file:', latest_runfile)
        self.setup_parallel_computation(latest_runfile, cores)

        run_file_dir = os.path.split(latest_runfile)[0]
        run_file_base_name = os.path.splitext(os.path.split(latest_runfile)[1])[0]
        batch_file = os.path.join(run_file_dir, run_file_base_name + '.batch')

        self.run_parallel_computation(batch_file)

    @staticmethod
    def run_parallel_computation(batch_path: str):
        fine.run_parallel_computation(batch_path)

    @property
    def name(self):
        return self.name

    @name.setter
    def name(self, value):
        if self.working_path is not None:
            existing_titles = os.listdir(self.working_path)
            if value not in existing_titles:
                self.name = value
            else:
                index = 0
                while True:
                    index += 1
                    new_title = value + f' ({index})'
                    if new_title not in existing_titles:
                        break
                self.name = new_title

            os.mkdir(os.path.join(self.working_path, self.name))

    @property
    def working_path(self):
        return self.working_path

    @working_path.setter
    def working_path(self, value):
        if os.path.exists(value):
            self.working_path = value
        else:
            try:
                os.mkdir(value)
            except Exception as e:
                print(f'"{value}" error: {e}')

    @property
    def geomturbo_path(self):
        return self.geomturbo_path

    @geomturbo_path.setter
    def geomturbo_path(self, value):
        if os.path.exists(value):
            self.geomturbo_path = value
        else:
            print(f'"{value}" does not exists')

    @property
    def iec_path(self):
        return self.iec_path

    @iec_path.setter
    def iec_path(self, value):
        if os.path.exists(value):
            self.iec_path = value
        else:
            print(f'"{value}" does not exists')

    @property
    def trb_path(self):
        return self.trb_path

    @trb_path.setter
    def trb_path(self, value):
        if os.path.exists(value):
            self.trb_path = value
        else:
            print(f'"{value}" does not exists')