# -*- mode: ruby -*-
# vi: set ft=ruby :

ENV['VAGRANT_DEFAULT_PROVIDER'] = 'libvirt'
Vagrant.configure("2") do |config|
  config.vm.box = "generic/ubuntu1804"
  config.vm.box_version = "2.0.0"
  config.vm.hostname = "pwman-dev"
  config.vm.define "pwman3-dev"
  config.vm.synced_folder "./", "/vagrant"
  config.vm.provision :shell, path: "provision_vagrant.sh"
  config.vm.provider :libvirt do |v|
    v.cpus=1
    v.memory=512
    v.storage_pool_name = 'vagrant'

  end
end
