Debugging environment for NFD
=============================

To create a 12.04 32-bit VM, just run

    vagrant up

After the instance is created, copy the coredump file to the VM either using `scp` or simply placing it in this folder (it will appear in the shared `/vagrant` folder inside the VM).

After that, ssh to the VM:

    vagrant ssh

And you can run coredump analysis.

Sample commands:

- To start analysis of coredump (e.g., when file `core.25328` placed in this folder)

        gdb /usr/bin/nfd /vagrant/core.25328

- To switch to the main thread and get hold of `runner` instance, use

        # to select thread #2 for analysis
        thread 2

        # to see what threads are available
        info threads

        # to jump call stack up
        up

        # to select a specific frame in the call stack of the selected thread
        frame 6

- When you are in the frame where `this` points to `Runner` instance, you can do various things

        # Print values of NameTree
        print this->m_nfd.m_forwarder.get()->m_nameTree

        # Print using python method (implemented in ndn_nfd/printers.py)
        python import ndn_gdb
        python ndn_gdb.dumpForwarder('this->m_nfd.m_forwarder')

        # Print a specific NameTree entry
        print this->m_nfd.m_forwarder.get()->m_nameTree.m_buckets[274].m_entry._M_ptr

        # To easy typing, you can assign value to a variable
        set $tree=this->m_nfd.m_forwarder.get()->m_nameTree
        set $entry = $tree.m_buckets[274].m_entry._M_ptr

        print $tree
        print *$entry

- If some initial commands are repeated every time you run gdb, you can add them to `~/.gdbinit` or specify in the command line

        gdb /usr/bin/nfd /vagrant/core.25328 -ex 'thread 2' -ex ' frame 6' -ex 'python import ndn_gdb' -ex 'python ndn_gdb.dumpForwarder("this->m_nfd.m_forwarder")'

- To create coredump of the running process in Linux:

        gcore <PROCESS-ID>
