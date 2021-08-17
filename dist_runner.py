import os
import shutil
import zipfile
from datetime import datetime

from generate_icons import IconsGenerator
from generate_init import InitGenerator
from generate_nodes import NodesGenerator
from package_manager import PackageManager


# TODO: Maybe refactor(Config/Util/Build)?
class Runner:
    def __init__(self,
                 base_path=f'{os.getcwd()}{os.path.sep}dist{os.path.sep}',
                 version=datetime.today().strftime("%y%m%d")):
        # Version to Build and Path for Outputs
        self.version = version
        self.base_path = base_path

        # Module Output Target
        target_dir = 'ladybug_tools'
        # Working Directory
        tmp_dir = 'working'

        # Paths for Build and Working Directories
        self.build_path = f'{base_path}{target_dir}{os.path.sep}'
        self.work_path = f'{base_path}{tmp_dir}{os.path.sep}'

        # Create the Package Downloader for the Runtime
        self.package = PackageManager(runtime=self)

    def destroy(self):
        if os.path.isdir(self.base_path):
            shutil.rmtree(self.base_path)

    def bootstrap(self):
        self.destroy()
        shutil.copytree('ladybug_tools', self.build_path)

    def clean(self):
        shutil.rmtree(self.work_path)

    def run(self):
        # Clean the directory on every run
        self.bootstrap()

        # Code Generation of Files
        InitGenerator(runtime=self).generate()

        # TODO: Add more packages
        # for pkgname in ['ladybug-grasshopper']:

        # Download Grasshopper and Load Schemas
        self.package.download(target='ladybug-grasshopper')
        self.package.load()

        IconsGenerator(runtime=self).generate()
        NodesGenerator(runtime=self).generate()

        self.clean()

    def package(self):
        # TODO: Replace __init__ Version Number
        z = zipfile.ZipFile(f'{self.build_path}ladybug-blender-{self.version}.zip', 'w')
        z.write(f"{self.build_path}ladybug_tools/")
        z.close()


# Run only if called from CLI
if __name__ == '__main__':
    rt = Runner()
    rt.run()
    # rt.package()
