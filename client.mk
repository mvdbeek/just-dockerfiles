# Client Makefile for just-dockerfiles testing framework.

# Absolute location of the configuration for the test framework.
JUST_DOCKERFILES_CONFIG?=$(CURDIR)/just-dockerfiles.json
export JUST_DOCKERFILES_CONFIG

# Absolute location of the just-dockerfiles git subdirectory.
JUST_DOCKERFILES_DIR?=$(CURDIR)/just-dockerfiles
export JUST_DOCKERFILES_DIR

# Call Makefile in just_dockerfiles proper.
JUST_DOCKERFILES_MAKE=$(MAKE) -C "$(JUST_DOCKERFILES_DIR)"

run-test:
	$(JUST_DOCKERFILES_MAKE) run-test $(MAKEFLAGS)

dump-description:
	$(JUST_DOCKERFILES_MAKE) dump-description $(MAKEFLAGS)
