# Author: Jose Luis Jorro-Aragoneses

'''
This module allows to import the communitu_module local library
in al examples. To do that, it is necessary to include the next
line in the import section of an example:

from .context import community_detection

'''

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import dao

