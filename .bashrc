#! /usr/bin/env bash
export SCM_PATH=$(dirname "$(realpath $0)")
export PYTHONPATH=$SCM_PATH/py
export PS1='\[\033[01;91m\]($name)\[\033[00m\] \[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '
