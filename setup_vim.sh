#!/bin/bash

sudo yum remove -y vim-common vim-enhanced
sudo yum install -y mercurial lua-devel ncurses-devel

cd /usr/local/src
sudo hg clone https://vim.googlecode.com/hg vim
cd vim
sudo hg pull
sudo hg update
sudo make distclean

# --prefix=/usr/local でもいいかも
# --with-ruby-command=/home/vagrant/.rbenv/shims/ruby RubyのPATH
sudo ./configure --prefix=/opt/vim  --with-features=huge --enable-multibyte --enable-rubyinterp --enable-luainterp --enable-cscope --enable-fail-if-missing --with-ruby-command=/usr/local/rbenv/shims/ruby --with-lua-prefix=/usr
sudo make
sudo make install

sudo ln -s /opt/vim/bin/vim /usr/local/bin/
