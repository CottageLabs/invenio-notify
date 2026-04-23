Development Installation
========================

1. Get yourself an InvenioRDM instance to install this module into.

2. Clone this module to your local environment

3. Create a virtual environment for development.  The virtual environment will need to be for python 3.12, and you may also need to install iPython, and upgrade pip

.. code-block:: bash

   python3.12 -m venv .venv
   source .venv/bin/activate
   pip install ipython
   pip install --upgrade pip

4. Install the module in development/editable mode:

.. code-block:: bash

   pip install -e .

5. Run through a regular invenio installation.  Short instructions

You may wish to delete any pre-existing Pipfile.lock at this point to avoid any confusion.

.. code-block:: bash

     pip install invenio-cli
     invenio-cli install
     invenio-cli services setup
     invenio-cli run

Note that we do not use the ``-N`` on setup, because we want some demo data to work with.

6. Create an admin user

.. code-block:: bash

    invenio users create admin@email.com --password <password> --active --confirm
    invenio access allow administration-access user admin@email.com

7. You can now set up a Notify actor/user using the instructions in `docs/getting_started.rst`

