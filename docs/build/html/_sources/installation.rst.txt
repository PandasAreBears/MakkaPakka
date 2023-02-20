**Installation**
================

.. note::
    Makka Pakka only works on Ubuntu. Other linux distribution may have when
    running 'source configure.sh'.

Installation
------------
To install, follow these steps:

.. code-block:: console

    cd <your directory>
    git clone https://github.com/PandasAreBears/MakkaPakka

.. code-block:: console

    cd MakkaPakka
    source configure.sh

At this point you can use Makka Pakka from within this directory.

.. code-block:: console

    python3 mkpk.py --help

To install as a program from anywhere, run the following from the MakkaPakka
root directory:

.. code-block:: console

    sudo ln -s ${PWD}/mkpk.py /usr/local/bin/mkpk.py
    echo "alias mkpk='python3 /usr/local/bin/mkpk.py'" >> ~/.bashrc
    source ~/.bashrc

Makka pakka can then be run from anywhere, test this by verifying the output
of:

.. code-block:: console

    mkpk --help


.. seealso::
    - :doc:`usage`
    - :doc:`examples`
    - :doc:`language_spec`
