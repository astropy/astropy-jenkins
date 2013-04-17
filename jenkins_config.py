"""
Configuration for the astropy Shining Panda tools.
"""
import os

# The versions of Python and Numpy to test.  The keys are versions of
# Python, the values are tuples of versions of Numpy to install into
# that version of Python.  The numpy version may be 'dev', in which
# case no Numpy version will be installed now, but a Jenkins build
# task will build and install Numpy from git.
versions = {
    2.6: (1.5, 1.6, 1.7),
    2.7: (1.5, 1.6, 1.7, 'dev'),
    3.2: (1.6, 1.7),
    3.3: (1.7, 'dev')
    }

# Defines the "main" virtualenv, which will be used to generate the
# docs, coverage reports, and other things which we don't need to run
# in every combination
main = (2.7, 1.7)

# Additional packages to install in each virtualenv
additional_packages = ['cython']

# Additional packages to install in the "main" virtualenv
main_packages = ['sphinx', 'pytest-cov', 'matplotlib']

# The root path for the virtual environments
root = os.path.expanduser('~')

# The root path of the system python interpreters.  This is specific
# to Shining Panda.
python_interpreter_path = '/sp/bin'

# The root URL of the astropy Jenkins dashboard website
root_url = "https://jenkins.shiningpanda.com/astropy/"

# A regular expression to match the builds that should have the matrix
# of Python and Numpy versions updated.
multiconfig_build_regex = '.*debian-multiconfig$'
