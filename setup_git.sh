#!/bin/bash

GIT_VER="2.9.2"
TIG_VER="2.1.1"

# Git
sudo yum -y remove git
sudo yum install -y gcc curl-devel expat-devel gettext-devel ncurses-devel openssl-devel zlib-devel perl-ExtUtils-MakeMaker

cd /usr/local/src
[ ! -e /usr/local/src/git-${GIT_VER}.tar.gz ] && sudo wget https://www.kernel.org/pub/software/scm/git/git-${GIT_VER}.tar.gz
[ ! -e /usr/local/src/git-${GIT_VER} ] && sudo tar zxvf git-${GIT_VER}.tar.gz

cd /usr/local/src/git-${GIT_VER}
[ ! -e /usr/local/bin/git ] && sudo ./configure --prefix=/usr/local/
[ ! -e /usr/local/bin/git ] && sudo make && sudo make install

# diff-highlight
# CentOS
sudo ln -s /usr/local/src/git-${GIT_VER}/contrib/diff-highlight/diff-highlight /usr/local/bin/diff-highlight
# Ubuntu
# sudo chmod 755 /usr/share/doc/git/contrib/diff-highlight/diff-highlight
# sudo ln -s /usr/local/src/git-${GIT_VER}/contrib/diff-highlight/diff-highlight /usr/local/bin/diff-highlight

# Tig
cd /usr/local/src
[ ! -e /usr/local/src/tig-${TIG_VER}.tar.gz ] && sudo wget http://jonas.nitro.dk/tig/releases/tig-${TIG_VER}.tar.gz
[ ! -e /usr/local/src/tig-${TIG_VER} ] && sudo tar zxvf tig-${TIG_VER}.tar.gz

cd /usr/local/src/tig-${TIG_VER}
[ ! -e /usr/local/bin/tig ] && sudo ./configure --prefix=/usr/local/
[ ! -e /usr/local/bin/tig ] && sudo make && sudo make install
