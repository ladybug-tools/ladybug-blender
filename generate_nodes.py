import os
import json
import pystache
import subprocess
from pathlib import Path

class Generator():
    def __init__(self):
        self.json_dir = './dist/working/json/'
        self.python2to3_bin = '/usr/bin/2to3'
        #self.out_dir = './nodes/ladybug/'
        self.out_dir = './dist/working/python/'

    def generate(self):
        for filename in Path(self.json_dir).glob('*.json'):
            if 'LB_Export_UserObject' in str(filename) \
                    or 'LB_Sync_Grasshopper_File' in str(filename) \
                    or 'LB_Versioner' in str(filename):
                continue # I think these nodes are just for Grasshopper
            with open(filename, 'r') as spec_f:
                self.generate_node(os.path.basename(filename), json.load(spec_f))

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
        spec['code'] = pystache.render(spec['code'].replace('\n', '\n' + ' '*8), code_data)
        spec['outputs'] = spec['outputs'][0] # JSON double nests this, maybe a mistake?
        spec['input_name_list'] = ', '.join(["'{}'".format(i['name']) for i in spec['inputs']])
        spec['input_name_unquoted_list'] = ', '.join([i['name'] for i in spec['inputs']])
        spec['input_type_list'] = ', '.join(["'{}'".format(i['type']) for i in spec['inputs']])
        spec['input_default_list'] = [repr(i['default']) for i in spec['inputs']]

        # These two lines are because the JSON dosen't properly represent bools
        spec['input_default_list'] = ['True' if i == "'true'" else i for i in spec['input_default_list']]
        spec['input_default_list'] = ['False' if i == "'false'" else i for i in spec['input_default_list']]

        spec['input_default_list'] = ', '.join(spec['input_default_list'])
        spec['input_access_list'] = ', '.join(["'{}'".format(i['access']) for i in spec['inputs']])
        spec['output_name_list'] = ', '.join(["'{}'".format(o['name']) for o in spec['outputs']])
        spec['nickname'] = spec['nickname'].replace('+', 'Plus')
        module_name = filename[0:-5]
        out_filepath = os.path.join(self.out_dir, module_name + '.py')
        with open(out_filepath, 'w') as f:
            with open('generic_node.mustache', 'r') as template:
                f.write(pystache.render(template.read(), spec))
        subprocess.run([self.python2to3_bin, '-x', 'itertools_imports', '-w', out_filepath])

generator = Generator()
generator.generate()
