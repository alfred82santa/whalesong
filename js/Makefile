PACKAGE_NAME = whalesongjs

help:
	@echo "Options"
	@echo "-----------------------------------------------------------------------"
	@echo "help:                     This help"
	@echo "requirements:             Download requirements"
	@echo "build:                    Build scriptlet"
	@echo "-----------------------------------------------------------------------"

requirements:
	@echo "Installing ${PACKAGE_NAME} requirements..."
	npm install --devDependencies

build:
	@echo "Building scriptlet..."
	npm run-script build

beautify:
	node node_modules/glob-run/bin/glob-run node node_modules/js-beautify/js/bin/js-beautify -r src/**/\*.js