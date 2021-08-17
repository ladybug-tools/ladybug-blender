import os

import pystache


class NodesGenerator:

    # TODO: Handle composition better for working paths
    def __init__(self, runtime):
        # Runtime Injection
        self.runtime = runtime

        # Output for Nodes
        self.out_dir = f'{runtime.build_path}nodes{os.path.sep}ladybug'

        # TODO: Resolve 2to3 and ImageMagick
        # self.python2to3_bin = shutil.which('2to3')
        # self.imagemagik_convert_bin = shutil.which('convert')

        # TODO: Handle missing bins
        # if not self.python2to3_bin:
        #     raise FileNotFoundError('2to3 is not installed in PATH!')

    def generate(self):
        # Each of the Package Schemas, keyed by filename
        for filename in self.runtime.package.schemas:
            if 'LB_Export_UserObject' in str(filename) \
                    or 'LB_Sync_Grasshopper_File' in str(filename) \
                    or 'LB_Versioner' in str(filename):
                continue  # I think these nodes are just for Grasshopper

            self.generate_node(f'{filename}.json', self.runtime.package.schemas[filename])

    def generate_node(self, filename, spec):
        code_data = {
            'cad': 'tools',
            'Cad': 'Blender Ladybug',
            'plugin': 'sverchok',
            'Plugin': '',
            'PLGN': '',
            'Package_Manager': ''
        }
        #    'grasshopper': '{{plugin}}', 'Grasshopper': '{{Plugin}}',
        #    'GH': '{{PLGN}}', 'Food4Rhino': '{{Package_Manager}}',
        #    'rhino': '{{cad}}', 'Rhino': '{{Cad}}'
        spec['code'] = pystache.render(spec['code'].replace('\n', '\n' + ' ' * 8), code_data)
        spec['outputs'] = spec['outputs'][0]  # JSON double nests this, maybe a mistake?
        spec['input_name_list'] = ', '.join(["'{}'".format(i['name']) for i in spec['inputs']])
        spec['input_name_unquoted_list'] = ', '.join([i['name'] for i in spec['inputs']])
        spec['input_type_list'] = ', '.join(["'{}'".format(i['type']) for i in spec['inputs']])
        spec['input_default_list'] = [repr(i['default']) for i in spec['inputs']]

        # These two lines are because the JSON doesn't properly represent booleans
        spec['input_default_list'] = ['True' if i == "'true'" else i for i in spec['input_default_list']]
        spec['input_default_list'] = ['False' if i == "'false'" else i for i in spec['input_default_list']]

        spec['input_default_list'] = ', '.join(spec['input_default_list'])
        spec['input_access_list'] = ', '.join(["'{}'".format(i['access']) for i in spec['inputs']])
        spec['output_name_list'] = ', '.join(["'{}'".format(o['name']) for o in spec['outputs']])
        spec['nickname'] = spec['nickname'].replace('+', 'Plus')
        spec['nickname_uppercase'] = spec['nickname'].upper()
        spec['description'] = spec['description'].replace('\n', ' ').replace("'", "\\'")
        for item in spec['inputs']:
            item['description'] = item['description'].replace('\n', ' ').replace("'", "\\'")
        for item in spec['outputs']:
            item['description'] = item['description'].replace('\n', ' ').replace("'", "\\'")
        module_name = filename[0:-5]
        out_filepath = os.path.join(self.out_dir, module_name + '.py')
        with open(out_filepath, 'w') as f:
            with open('generic_node.mustache', 'r') as template:
                f.write(pystache.render(template.read(), spec))
        # TODO: Implement Python 2to3
        # subprocess.run([self.python2to3_bin, '-x', 'itertools_imports', '-w', out_filepath])


# Run only if called from CLI
if __name__ == '__main__':
    from dist_runner import Runner

    NodesGenerator(runtime=Runner()).generate()
