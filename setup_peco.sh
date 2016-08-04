#!/bin/bash

PECO_VER="0.3.6"

cd /usr/local/src

[ ! -e /usr/local/src/peco_linux_amd64.tar.gz ] && sudo wget https://github.com/peco/peco/releases/download/v${PECO_VER}/peco_linux_amd64.tar.gz
[ ! -e /usr/local/src/peco_linux_amd64 ] && sudo tar zxvf peco_linux_amd64.tar.gz
[ ! -e ~/.peco/config.json ] && mkdir $HOME/.peco && ln -s $HOME/dotfiles/config.json $HOME/.peco

sudo ln -s /usr/local/src/peco_linux_amd64/peco /usr/local/bin
