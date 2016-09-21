#!/bin/bash

set -e
set -x

cd `dirname $0`

RECIPE_DIRECTORY="tests/recipes"
export RECIPE_DIRECTORY

py.test --tb=native run_test.py -k 'test_test1'
! py.test --tb=native run_test.py -k 'test_test2'
