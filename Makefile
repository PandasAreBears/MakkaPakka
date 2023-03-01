
package_test: clean build deploy_test

package: clean build deploy

deploy_test:
	twine upload -r testpypi dist/*

deploy:
	twine upload dist/*

clean:
	rm -rf dist

build:
	python3 -m build
