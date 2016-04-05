#!/bin/bash

ZSH_VER="5.2"

sudo yum install -y ncurses-devel

cd /usr/local/src
[ ! -e /usr/local/src/zsh-${ZSH_VER}.tar.gz ] && sudo wget http://downloads.sourceforge.net/project/zsh/zsh/${ZSH_VER}/zsh-${ZSH_VER}.tar.gz
[ ! -e /usr/local/src/zsh-${ZSH_VER} ] && sudo tar zxvf zsh-${ZSH_VER}.tar.gz

cd /usr/local/src/zsh-${ZSH_VER}
[ ! -e /usr/local/bin/zsh ] && sudo ./configure
[ ! -e /usr/local/bin/zsh ] && sudo make && sudo make install

sudo sh -c "echo '/usr/local/bin/zsh' >> /etc/shells"
chsh -s /usr/local/bin/zsh
