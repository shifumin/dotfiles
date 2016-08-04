#!/bin/bash

RUBY_VER="2.3.1"

sudo yum remove -y vim-common vim-enhanced
sudo yum install -y mercurial lua-devel ncurses-devel readline-devel python-devel

git clone git@github.com:sstephenson/rbenv.git ~/.rbenv
git clone git@github.com:sstephenson/ruby-build.git ~/.rbenv/plugins/ruby-build
rbenv install ${RUBY_VER}
rbenv rehash
rbenv global ${RUBY_VER}

cd /usr/local/src
sudo hg clone https://bitbucket.org/vim-mirror/vim
cd vim
sudo hg pull
sudo hg update
sudo make distclean

# --prefix=/usr/local でもいいかも
# --with-ruby-command=~/.rbenv/shims/ruby RubyのPATH
sudo ./configure --prefix=/opt/vim  --with-features=huge --enable-multibyte --enable-rubyinterp --enable-pythoninterp --enable-luainterp --enable-cscope --enable-fail-if-missing --with-ruby-command=~/.rbenv/shims/ruby --with-lua-prefix=/usr
sudo make
sudo make install

sudo ln -s /opt/vim/bin/vim /usr/local/bin/
