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


def replace(file_path, pattern, subst):

    """ 
    Open file, find pattern in file and replace it with substitute

    Inputs:
        - file_path: path of file to edit
        - pattern: string of pattern to replace 
        - subst: substitution string for the replaced pattern
    """

    with open(file_path, 'r') as f:
        file_string = f.read()

    file_string = (re.sub(pattern, subst, file_string))

    with open(file_path, 'w') as f:
        f.write(file_string)


def convert_input_to_list(input_file):
    if isinstance(input_file, str):
        with open(input_file, 'r') as f:
            input_list = f.readlines()
    elif isinstance(input_file, (list, tuple)):
            input_list = input_file
    else:
        raise TypeError('Provide the input file either as path pointing '
                        'to file or as tuple or list with its content')
    return input_list


def read_foam_header(input_file):

    """
    Extract the OpenFOAM header from input file

    Inputs:
        - input_file: OF-input file path or list of file lines
    Returns:
        - header: list of lines comprising the specific OF-file header
    """

    input_list = convert_input_to_list(input_file)
    header = []
    for line in input_list:
        header.append(line)
        if re.search('^// *') in line:
            break
    return header


def read_first_dict(input_file):

    """ 
    Extract the first and highest dictionary in hierarchy
    in OpenFOAM (OF) format from provided list 

    Inputs:
        - input_file: OF-input file path or list of file lines
    Returns:
        - name: name of OF-dict
        - content: list of lines of the OF-dict
        - found_dict: bool to indicate whether a dictionary was found
        - rem_list: remaining list following the first dictionary
    """

    input_list = convert_input_to_list(input_file)
    open_braces = 0
    found_dict = False
    content = []
    end_id = -1
    name = ''
    for i, line in enumerate(input_list):
        if open_braces == 0 and '{' in line:
            found_dict = True
            name = input_list[i - 1].strip()
            open_braces += 1
        elif open_braces > 0 and '{' in line:
            open_braces += 1
            content.append(line)
        elif open_braces > 1 and '}' in line:
            open_braces -= 1
            content.append(line)
        elif open_braces > 0:
            content.append(line)
        else:
            end_id = i
            break
    rem_list = input_list[end_id + 1:]

    return name, content, found_dict, rem_list


def read_dict(dict_name, input_file):

    """
    Extract the dictionary dict_name
    in OpenFOAM (OF) format from provided list

    Inputs:
        - dict_name: name of dictionary as string
        - input_file: OF-input file path or list of file lines
    Returns:
        - name: name of OF-dict
        - content: list of lines of the OF-dict
        - found_dict: bool to indicate whether a dictionary was found
        - rem_list: remaining list following the first dictionary
    """

    input_list = convert_input_to_list(input_file)
    found_dict = False
    content = []
    for i, line in enumerate(input_list):
        if dict_name in line:
            input_list = input_list[i:]
        dict_name, content, found_dict, rem_list = \
            read_first_dict(input_list)

    return content, found_dict, rem_list


def read_all_dicts(input_file):

    """ 
    Extract all OpenFOAM dictionaries in highest hierarchy
    in OpenFOAM (OF) format from list 

    Inputs:
        - input_file: OF-input file path or list of file lines
    Returns:
        - dicts: python dictionary with OF-dictionary names as keys
                 and content string list as values
    """

    input_list = convert_input_to_list(input_file)
    dicts = {}
    found_dict = True
    while found_dict is True:
        name, content, found_dict, input_list = read_first_dict(input_list)
        dicts[name] = content
    return dicts


def read_boundary_conditions(input_file):

    """ 
    Extract boundary condition data from an OF field file

    Inputs:
        - input_file: OF-input file path or list of file lines
    Returns:
        - bc_dict: python dictionary containing bc patch dictionaries
    """

    input_list = convert_input_to_list(input_file)
    header = read_foam_header(input_list)
    bc_dict = {'header': header}

    input_list = input_list[len(header):]
    input_list_no_comments = \
        [line for line in input_list if not re.search('^\s*//')]

    for line in input_list_no_comments:
        if 'dimensions' in line:
            bc_dict['dimensions'] = line
        if 'internalField' in line:
            bc_dict['internalField'] = line

    file_dicts = read_all_dicts(input_list)
    bf_list = file_dicts['boundaryField']
    bc_dict.update(read_all_dicts(bf_list))

    return bc_dict


def read_transport_properties(input_file):

    """ 
    Extract transport properties data from the
    OpenFOAM transportProperties file

    Inputs:
        - input_file: OF-input file path or list of file lines
    Returns:
        - tp_dict: python dictionary containing
                   transport models and dictionaries
    """
        
    input_list = convert_input_to_list(input_file)
    header = read_foam_header(input_list)
    tp_dict = {'header': header}

    input_list = input_list[len(header):]
    input_list_no_comments = \
        [line for line in input_list if not re.search('^\s*//')]

    for line in input_list_no_comments:
        if 'transportModel' in line:
            tp_dict['transportModel'] = line.split()[1][:-1]
        if 'rheologyModel' in line:
            tp_dict['rheologyModel'] = line.split()[1][:-1]
        if 'structureModel' in line:
            tp_dict['structureModel'] = line.split()[1][:-1]

    rem_list = input_list_no_comments
    for key in tp_dict:
        dict_name = key+'Coeffs'
        content, rem_list = read_dict(dict_name, rem_list)
        tp_dict[dict_name] = content

    return tp_dict


def construct_foam_dict(in_dict):

    """
    Construct consecutive OpenFOAM dictionaries from python dictionary

    Inputs:
        - in_dict: python dictionary with dictionary names as keys
                 and content list as values
    Returns:
        - dict_list: OpenFOAM dictionaries as list of strings
    """

    if not isinstance(in_dict, dict):
        raise TypeError('Provide the foam dictionaries as a python dictionary '
                        'with the dictionary names as keys '
                        'and the content in a list of strings as values')

    dict_list = []
    for key in in_dict:
        content = in_dict[key]
        content_indentation = len(content[0]) - len(content[0].lstrip())
        dict_indentation = max(0, content_indentation - FOAM_TAB_SIZE)
        name_str = key.rjust(len(key) + dict_indentation) + '\n'
        dict_list.append(name_str)
        dict_list.append('{'.rjust(1 + dict_indentation) + '\n')
        dict_list.extend(content)
        dict_list.append('}'.rjust(1 + dict_indentation) + '\n')

    return dict_list
