#!/bin/bash

sudo yum -y remove git
sudo yum install -y gcc curl-devel expat-devel gettext-devel openssl-devel zlib-devel perl-ExtUtils-MakeMaker

sudo cd /usr/local/src
sudo wget https://www.kernel.org/pub/software/scm/git/git-2.7.0.tar.gz
sudo tar zxvf git-2.7.0.tar.gz

sudo cd git-2.7.0/
sudo ./configure --prefix=/usr/local/
sudo make $$ make install

sudo ln -s /usr/local/src/git-2.7.0/contrib/diff-highlight/diff-highlight /usr/lolca/bin/diff-highlight
