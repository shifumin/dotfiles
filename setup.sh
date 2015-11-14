#!/bin/bash

# install dotfiles
DOT_FILES=( .ansible.cfg .ctags .gemrc .gitconfig .gitignore .pryrc .rubocop.yml .tmux.conf .vimrc .vimrc.neobundle .zshrc .zshrc.custom .zshenv)
for file in ${DOT_FILES[@]}
do
    ln -s $HOME/dotfiles/$file $HOME/$file
done

# install bin for tmux
BIN_FILES=( battery )
for file in ${BIN_FILES[@]}
do
    ln -s $HOME/dotfiles/$file /usr/local/bin/$file
done

# install .vim/indent/ruby.vim
[ ! -d ~/.vim/indent ] && mkdir ~/.vim/indent && ln -s $HOME/dotfiles/ruby.vim $HOME/.vim/indent/ruby.vim

# install oh-my-zsh
[ ! -d ~/.oh-my-zsh ] && git clone git://github.com/robbyrussell/oh-my-zsh.git ~/.oh-my-zsh

# install NeoBundle
[ ! -d ~/.vim/bundle ] && mkdir -p ~/.vim/bundle && git clone git://github.com/Shougo/neobundle.vim ~/.vim/bundle/neobundle.vim && echo "you should run following command to setup plugins ->  vim -c ':NeoBundleInstall'"

