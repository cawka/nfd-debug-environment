# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"

$SCRIPT = <<MSG
  add-apt-repository -y ppa:named-data/ppa
  apt-get update

  apt-get install -y build-essential vim emacs python python-dev git subversion python-setuptools libssl-dev libffi-dev flex texinfo bison
  apt-get install -y nfd nfd-dbg ndn-cxx-dev ndn-cxx-dbg ndn-tools

  easy_install pip
  pip install cryptography
  pip install pyndn

  # git clone https://github.com/ruediger/Boost-Pretty-Printer.git /opt/gdb-boost
  git clone -b merge-attempt https://github.com/mateidavid/Boost-Pretty-Printer /opt/gdb-boost
  git clone https://github.com/koutheir/libcxx-pretty-printers.git /opt/gdb-libcxx
  svn co https://gcc.gnu.org/svn/gcc/trunk/libstdc++-v3/python /opt/gdb-libstdcxx

  cd /tmp
  git clone --depth=1 git://sourceware.org/git/binutils-gdb.git
  cd binutils-gdb
  ./configure --with-python=/usr/bin/python
  make
  make install
  cd /tmp
  rm -Rf binutils-gdb

  cd /usr/src
  apt-get source ndn-cxx nfd
  rm ndn-cxx_* nfd_*

  sudo -u vagrant sh -c "\
    touch /home/vagrant/.gdbinit.local; \
    echo 'source /vagrant/gdbinit-user-friendly' >> /home/vagrant/.gdbinit; \
    echo 'source /vagrant/gdbinit-printers' >> /home/vagrant/.gdbinit ;\
    echo 'set debug-file-directory /usr/local/lib/debug:/usr/lib/debug' >> /home/vagrant/.gdbinit ;\
    echo 'set dir \$cdir:\$cwd:$(eval echo "/usr/src/ndn-cxx-*")/src:$(eval echo "/usr/src/nfd-*")/daemon' >> /home/vagrant/.gdbinit ;\
   "
MSG

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "ubuntu/precise32"
  config.vm.provision "shell", inline: $SCRIPT

  config.vm.provider "virtualbox" do |vb|
    # vb.gui = true
    vb.cpus = 1
    vb.memory = 3048
  end
end
