#!/usr/bin/env python2.7
"""
This script sets up and/or updates all of the virtualenvs required for
the astropy builds on Shining Panda.

It is not intended to be terribly useful outside of Shining Panda,
since it assumes that all of the desired versions of Python are
already built and installed somewhere on the machine.

The script may be re-run periodically to update the dependencies in
each virtual environment.
"""

import os
import shutil
import subprocess
import sys

import jenkins_config as config


def run_command(args):
    """
    A thin wrapper around `subprocess.call`, that runs the given list
    of arguments.
    """
    print("   > {0}".format(' '.join(args)))
    with open(os.devnull, "w") as fnull:
        result = subprocess.call(
            ' '.join(args), stdout=fnull, stderr=fnull, shell=True)
    if result != 0:
        print('FAILED')
        sys.exit(1)


def create_environment(name, python_version, pip_installs):
    """
    Creates a new virtual environment.

    Parameters
    ----------
    name : str
        The name of the environment

    python_version : str
        The Python version to use for the environment.  Must be
        `major.minor` only, not `major.minor.maint`.

    pip_installs : list of str
        A list of packages to install with pip.  Each entry may
        contain pip version specifiers as well.
    """
    print("Environment {0}".format(name))

    system_python_path = os.path.join(
        config.python_interpreter_path,
        'python{0}'.format(python_version))

    path = os.path.join(config.root, name)

    # If the environment already exists, we need to verify that it is
    # the *exact* same version of Python as the available system
    # Python, otherwise we delete it and start over.
    if os.path.exists(path):
        # If the version is not an exact match, we need to blitz the
        # environment and start over.
        virtual_bin = os.path.join(path, 'bin', 'python')
        if os.path.exists(virtual_bin):
            virtual_ver = subprocess.check_output(
                '{0} --version'.format(virtual_bin),
                shell=True)
        else:
            virtual_ver = None
        system_ver = subprocess.check_output(
            '{0} --version'.format(system_python_path),
            shell=True)

        if virtual_ver != system_ver:
            print(
                "   Removing virtualenv {0} since it is out-of-date or broken".format(
                name))
            shutil.rmtree(path)

    if not os.path.exists(path):
        run_command(
            [system_python_path,
             os.path.join(os.path.dirname(__file__), 'virtualenv.py'),
             path])

    for pip_install in pip_installs:
        run_command(
            [os.path.join(path, 'bin', 'pip'),
             'install',
             '--upgrade',
             pip_install])


def create_all_environments():
    """
    Creates all of the environments as specified in the configuration.
    """
    for python, numpys in sorted(config.versions.items()):
        for numpy in numpys:
            name = 'env{0}-numpy{1}'.format(python, numpy)
            pip_installs = []
            if numpy != 'dev':
                pip_installs.append(
                    "'numpy>={0},<{1}'".format(numpy, numpy + 0.1))
            pip_installs.extend(config.additional_packages)
            if python, numpy == config.main:
                pip_installs.extend(config.main_packages)
            create_environment(name, python, pip_installs)

            # Create a symlink for the main environment
            if python, numpy == config.main:
                main_env = os.path.join(config.root, 'env-main')
                if os.path.exists(main_env):
                    os.remove(main_env)
                os.symlink(os.path.join(config.root, name), main_env)

    create_environment('env-nocython', '2.7', ['numpy'])


if __name__ == '__main__':
    create_all_environments()
