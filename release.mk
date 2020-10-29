PY ?= python3
PACKAGE ?= $(shell basename $(CURDIR))

check-env:
ifndef VER
	$(error VER is undefined)
endif


release/start: check-env
	@echo "checking out branch prepare_"$(VER)
	@git checkout -b prepare_$(VER)
	sudo rm -Rf $(PACKAGE).egg-info dist/
	@echo "create a git tag"
	@git tag -s $(VER) -m "tmp-tag"
	$(PY) setup.py sdist
	@echo "Edit TAGMESSAGE and Update ChangeLog"
	@echo "After that continue with: make release/complete"

do-bump: NVER = $(subst v,,$(VER))
do-bump: check-env
	echo $(NVER)
	sed -i "s/version =[[:space:]]'[[:digit:]]\+\.[[:digit:]]\+\.[[:digit:]]'\+/version = '$(NVER)'/g" $(PACKAGE)/__init__.py

release/abort: check-env
	git checkout develop
	git branch -D prepare_$(VER) || echo "branch not found"
	git tag -d $(VER) || echo "tag not found"
	git push --delete origin $(VER)

do-release: do-bump
	git add $(PACKAGE)/__init__.py ChangeLog
	git commit -m "Bump version to $(VER)"
	git checkout master
	git merge prepare_$(VER) --ff
	git tag -f -s $(VER) -F TAGMESSAGE
	git push origin master --tags


release/complete: do-release finish-release
	echo "finished release"

release/finish: check-env
	git checkout develop
	git branch -D prepare_$(VER)
	git merge --ff master
	rm -f TAGMESSAGE
	git pull
	git push origin develop

# vim: tabstop=4 shiftwidth=4
