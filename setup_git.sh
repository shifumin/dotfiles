#!/bin/bash

GIT_VER="2.7.0"

sudo yum -y remove git
sudo yum install -y gcc curl-devel expat-devel gettext-devel openssl-devel zlib-devel perl-ExtUtils-MakeMaker

cd /usr/local/src
[ ! -e /usr/local/src/git-$GIT_VER.tar.gz ] && sudo wget https://www.kernel.org/pub/software/scm/git/git-$GIT_VER.tar.gz
[ ! -e /usr/local/src/git-$GIT_VER ] && sudo tar zxvf git-$GIT_VER.tar.gz

cd /usr/local/src/git-$GIT_VER
[ ! -e /usr/local/bin/git ] && sudo ./configure --prefix=/usr/local/
[ ! -e /usr/local/bin/git ] && sudo make && sudo make install

sudo ln -s /usr/local/src/git-$GIT_VER/contrib/diff-highlight/diff-highlight /usr/local/bin/diff-highlight
