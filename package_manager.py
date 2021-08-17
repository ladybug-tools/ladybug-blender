import glob
import io
import os
import shutil
import zipfile
import json

from pathlib import Path
import requests


# TODO: Test https://github.com/ladybug-tools/honeybee-grasshopper-core
class PackageManager:
    """Download Specifications and Icons for Ladybug-Blender"""

    def __init__(
            self,
            runtime,
    ):
        self.runtime = runtime
        self.json_path = f'{runtime.work_path}json'
        self.icon_path = f'{runtime.work_path}icon'
        self.schemas = {

        }

    def download(self, target):
        # Create scaffolding
        os.makedirs(self.json_path)
        os.makedirs(self.icon_path)

        # TODO: Pull by Version or use Git directly maybe?
        # Download Path and Globs
        dl_unzip_path = f'{self.runtime.work_path}{target}-master{os.path.sep}'
        dl_json_glob = f'{dl_unzip_path}{target.replace("-", "_")}{os.path.sep}json{os.path.sep}*.json'
        dl_icon_glob = f'{dl_unzip_path}{target.replace("-", "_")}{os.path.sep}icon{os.path.sep}*.png'

        # Set the Target URL
        target_url = f'https://github.com/ladybug-tools/{target}/archive/master.zip'

        # Unzip Target
        zipfile.ZipFile(io.BytesIO(requests.get(target_url).content)).extractall(self.runtime.work_path)

        # Copy Schema Files
        for file in glob.glob(dl_json_glob):
            shutil.copy(file, self.json_path)

        # Copy Icon Files
        for file in glob.glob(dl_icon_glob):
            shutil.copy(file, self.icon_path)

        # Cleanup Files
        shutil.rmtree(dl_unzip_path)

    def load(self):
        # Clear Data
        self.schemas.clear()

        # For each of the files downloaded
        for filename in Path(self.json_path).glob('*.json'):
            # Filter for unnecessary nodes
            if 'LB_Export_UserObject' in str(filename) \
                    or 'LB_Sync_Grasshopper_File' in str(filename) \
                    or 'LB_Versioner' in str(filename):
                continue  # I think these nodes are just for Grasshopper

            # Open file and store in schemas
            with open(filename, 'r') as spec_f:
                spec = json.load(spec_f)
                key = os.path.basename(filename).replace('.json', '')
                self.schemas[key] = spec
                self.schemas[key]['nickname'] = spec['nickname'].replace('+', 'Plus')


    def clean(self):
        if os.path.isdir(self.json_path):
            shutil.rmtree(self.json_path)
        if os.path.isdir(self.icon_path):
            shutil.rmtree(self.icon_path)


# Run only if called from CLI and pass in arguments
if __name__ == '__main__':
    import sys
    from dist_runner import Runner

    package = PackageManager(runtime=Runner())
    package.clean()
    package.download(target='ladybug-grasshopper' if len(sys.argv) == 1 else sys.argv[1])
    package.load()
    print(package.schemas)