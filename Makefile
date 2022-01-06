VERSION:=`date '+%y%m%d'`

.PHONY: dist
dist:
	rm -rf dist
	mkdir -p dist/ladybug_tools
	cp -r ladybug_tools/* dist/ladybug_tools/

	mkdir dist/working
	mkdir dist/working/json
	mkdir dist/working/icon
	mkdir dist/working/python
	cd dist/working && wget https://github.com/ladybug-tools/ladybug-grasshopper/archive/master.zip
	cd dist/working && unzip master.zip
	cd dist/working/json && cp -r ../ladybug-grasshopper-master/ladybug_grasshopper/json/*.json ./
	cd dist/working/icon && cp -r ../ladybug-grasshopper-master/ladybug_grasshopper/icon/*.png ./
	python -m venv dist/working/env
	source dist/working/env/bin/activate && pip install pystache
	source dist/working/env/bin/activate && python generate_init.py
	cp -r dist/working/python/* dist/ladybug_tools/
	rm -rf dist/working/python/*
	source dist/working/env/bin/activate && python generate_nodes.py
	cp -r dist/working/python/* dist/ladybug_tools/nodes/ladybug/
	cp -r dist/working/icon/* dist/ladybug_tools/icons/
	rm -rf dist/working

	mkdir dist/working
	python -m venv dist/working/env
	source dist/working/env/bin/activate && pip install lbt-ladybug
	cp -r dist/working/env/lib/python3.9/site-packages/ladybug dist/ladybug_tools/lib/
	cp -r dist/working/env/lib/python3.9/site-packages/ladybug_comfort dist/ladybug_tools/lib/
	cp -r dist/working/env/lib/python3.9/site-packages/ladybug_geometry dist/ladybug_tools/lib/
	rm -rf dist/working

	cd dist/ladybug_tools && sed -i "s/999999/$(VERSION)/" __init__.py
	cd dist && zip -r ladybug-blender-$(VERSION).zip ./*
	rm -rf dist/ladybug_tools

.PHONY: clean
clean:
	rm -rf dist
