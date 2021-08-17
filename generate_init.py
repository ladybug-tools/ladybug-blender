import os

import pystache


class InitGenerator:
    def __init__(self, runtime):
        self.runtime = runtime

    def generate(self):
        data = {
            'nodes': [],
            'subcategories': []
        }
        subcategories = {}

        # Build Data Dictionary
        for node_name in self.runtime.package.schemas:
            spec = self.runtime.package.schemas[node_name]
            filename = f'{node_name}.json'
            data['nodes'].append({
                'node_module': filename[0:-5],
                'node_classname': spec['nickname']
            })
            subcategory = spec['subcategory'].split(' :: ')[1]
            subcategories.setdefault(subcategory, []).append(spec['nickname'])

        # Build Subcategories Dictionary
        for name, nodes in subcategories.items():
            data['subcategories'].append({
                'name': name.replace(' ', '_'),
                'title': name,
                'nodes': nodes
            })

        # Save init to build path
        out_filepath = os.path.join(self.runtime.build_path, '__init__.py')
        with open(out_filepath, 'w') as f:
            with open('init.mustache', 'r') as template:
                f.write(pystache.render(template.read(), data))


if __name__ == '__main__':
    import sys
    from dist_runner import Runner

    _runtime = Runner()
    _runtime.clean()
    _runtime.package.clean()
    _runtime.package.download(target='ladybug-grasshopper' if len(sys.argv) == 1 else sys.argv[1])
    InitGenerator(runtime=_runtime).generate()
