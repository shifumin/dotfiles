#!/bin/bash

PECO_VER="0.3.5"

cd /usr/local/src

[ ! -e /usr/local/src/peco_linux_amd64.tar.gz ] && sudo wget https://github.com/peco/peco/releases/download/v${PECO_VER}/peco_linux_amd64.tar.gz
[ ! -e /usr/local/src/peco_linux_amd64 ] && sudo tar zxvf peco_linux_amd64.tar.gz

sudo ln -s /usr/local/src/peco_linux_amd64/peco /usr/local/bin