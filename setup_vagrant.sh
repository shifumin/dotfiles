#!/bin/bash

VAGRANT_PLUGINS=( sahara vagrant-vbguest vagrant-vbox-snapshot )

for plugin in ${VAGRANT_PLUGINS[@]}
do
    vagrant plugin install $plugin
done
