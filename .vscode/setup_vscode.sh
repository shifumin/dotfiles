#!/bin/sh

# settings
ln -is $HOME/dotfiles/.vscode/settings.json $HOME/Library/Application\ Support/Code/User/
ln -is $HOME/dotfiles/.vscode/keybindings.json $HOME/Library/Application\ Support/Code/User/

# install extentions
cat $HOME/dotfiles/.vscode/list-extensions | while read line
do
  code --install-extension $line
done
