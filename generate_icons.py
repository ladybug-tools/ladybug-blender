import os
from distutils.dir_util import copy_tree


class IconsGenerator:
    def __init__(self, runtime):
        self.runtime = runtime
        self.out_path = f"{self.runtime.build_path}icons{os.path.sep}"

    def generate(self):
        # Copy Icons from Package Downloader to the build path
        copy_tree(
            self.runtime.package.icon_path,
            self.out_path
        )
        # Loop through the modules
        for module_name in self.runtime.package.schemas:
            spec = self.runtime.package.schemas[module_name]
            icon_path = os.path.join(self.runtime.package.icon_path, 'lb_{}.png'.format(spec['nickname'].lower()))
            os.rename(
                os.path.join(self.runtime.package.icon_path, '{}.png'.format(module_name.replace('_', ' '))),
                icon_path)
            # This incantation reverts the intensity channel in HSI.
            # It will make light colors darker, and dark colors lighter
            # TODO: Implement ImageMagick
            # subprocess.run([
            #     'convert',
            #     icon_path,
            #     '-colorspace',
            #     'HSI',
            #     '-channel',
            #     'B',
            #     '-level',
            #     '100,0%',
            #     '+channel',
            #     '-colorspace',
            #     'sRGB',
            #     icon_path
            # ])
