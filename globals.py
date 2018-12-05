#!/usr/bin/env python

import os
import re

# Global constants
FOAM_TAB_SIZE = 4

# Global regular expressions for general number and OpenFOAM patterns
num_pattern = '[-+]?(?:(?:\d*\.\d+)|(?:\d+\.?))(?:[Ee][+-]?\d+)?'
re_num = re.compile(num_pattern)
of_dim_pattern = '\s*\[\s*([-+]?\d\s*)*\]\s*'
re_of_dim = re.compile(of_dim_pattern)
of_vec_pattern = \
    '\(\s*'+num_pattern+'\s*'+num_pattern+'\s*'+num_pattern+'\s*\)'
of_uni_vec_pattern = '\s*uniform\s*' + of_vec_pattern
re_uni_vec = re.compile(of_uni_vec_pattern)