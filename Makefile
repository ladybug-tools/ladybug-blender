VERSION:=`date '+%y%m%d'`
SHELL:= /bin/bash
.PHONY: dist
dist:
	python generate_dist.py
	#TODO: Move Packaging to its own
	mkdir dist/working
	python -m venv dist/working/env
	source dist/working/env/bin/activate && pip install lbt-ladybug
	#TODO: Find site-packages in current venv
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
