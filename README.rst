Astropy Shining Panda Scripts
=============================

This repository contains a set of scripts for managing the
configuration of Debian builds on Shining Panda.  This stuff is
probably only of use within the Shining Panda Debian environment and
not on Jenkins in general.

1) The configuration is stored in the file `jenkins_config.py`.  Edit
   that file to change the set of Python and Numpy versions to be
   tested.

2) The `setup_jenkins_virtualenvs.py` script is intended to be run
   inside of ShiningPanda's shell environment.

   The first time it is run, it will create all of the virtualenvs
   needed for the builds, each containing a particular combination
   of Python and Numpy.

   On subsequent runs, all of the versions of software installed in
   the virtualenvs (including any point releases of Python itself)
   will be updated if necessary.

3) The `update_build_configs.py` script will update all of the
   `debian-multiconfig` build configurations to include all of the
   versions of Python and Numpy specified in the configuration, by
   updating the `config.xml` files of each build independently.

   Since it uses the Jenkins web API, it may be run on any machine
   with access to the Internet.  The script will prompt you for your
   ShiningPanda username and password, which is used to authenticate
   over HTTPS.
