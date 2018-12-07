#!/usr/bin/env python

import os
import re
import globals as gl
import file_io_functions as fio

FLOAT_NUMBER_PATTERN = '[-+]?(?:(?:\d*\.\d+)|(?:\d+\.?))(?:[Ee][+-]?\d+)?'


class FoamDimensions(str):

    """
    Subclass of python string to extract OpenFOAM dimension set from basic
    string. If OpenFOAM dimensions were found in input_str, the constructor
    returns string with the stripped dimensions in square brackets.
    Example: '[0 2 -1 0 0 0 0]'
    If dimension pattern was not found, the constructor returns an empty string
    """

    FOAM_DIM_PATTERN = '\s*\[\s*([-+]?\d\s*)*\]\s*'
    RE_DIM = re.compile(FOAM_DIM_PATTERN)

    def __new__(cls, input_str):
        dim_match = cls.RE_DIM.match(input_str)
        if dim_match:
            dim_str = dim_match.group[0].lstrip().rstrip()
        else:
            dim_str = ''
        return super().__new__(cls, dim_str)


class FoamList:

    """
    Subclass of python string to extract OpenFOAM list from basic string
    or list. If OpenFOAM vector was found in input_str, the constructor returns
    string with the stripped list in round brackets.
    Example: '(0 0 0)'
    If list pattern was not found, the constructor returns an empty string
    """

    OPEN = '('
    CLOSE = ')'

    def __init__(self, input_data, delim = ' '):
        self.name = ''
        self.content = []
        self.delim = delim


    @classmethod
    def read(cls, input_data, delim = ' '):

        """
        Read the last and most inner nested list
        in OpenFOAM (OF) format from provided data

        Inputs:
            - input_data: OF-input data string, list or tuple
            - delim: delimiter symbol separating list items (default: ' ')
        Returns:
            - name: name of OF-list
            - data: python list of list entries
            - rem_data: remaining data not containing extracted list
        """

        data = fio.convert_input_to_str(input_data, delim)
        name = ''
        data = ''
        rem_data = ''
        lists = {}
        while cls.OPEN in data:
            data = data.split(cls.OPEN, 1)
            rem_data += data[0] + cls.OPEN
            lists.append(data[1])
        name = rem_data.split()[-1]
        if cls.CLOSE in data:
            data = data.split(cls.CLOSE, 1)[0].split(delim)

        return name, data, rem_data





        open_braces = 0
        found_dict = False
        content = []
        end_id = -1
        name = ''
        for i, line in enumerate(input_list):
            if open_braces == 0 and cls.OPEN in line:
                found_dict = True
                name = input_list[i - 1].strip()
                open_braces += 1
            elif open_braces > 0 and cls.OPEN in line:
                open_braces += 1
                content.append(line)
            elif open_braces > 1 and cls.CLOSE in line:
                open_braces -= 1
                content.append(line)
            elif open_braces > 0:
                content.append(line)
            else:
                end_id = i
                break
        rem_list = input_list[end_id + 1:]
        return name, content, found_dict, rem_list


class FoamVector(str):

    """
    Subclass of python string to extract OpenFOAM vector from basic string. If
    OpenFOAM vector was found in input_str, the constructor returns string with
    the stripped vector in round brackets.
    Example: '( 0 0 0 )'
    If vector pattern was not found, the constructor returns an empty string
    """

    FOAM_VECTOR_PATTERN = '\(\s*' + FLOAT_NUMBER_PATTERN \
                          + '\s*' + FLOAT_NUMBER_PATTERN \
                          + '\s*' + FLOAT_NUMBER_PATTERN + '\s*\)'
    RE_VECTOR = re.compile(FOAM_VECTOR_PATTERN)

    def __new__(cls, input_str):
        vector_match = cls.RE_DIM.match(input_str)
        if vector_match:
            vector_str = vector_match.group[0].lstrip().rstrip()
        else:
            vector_str = ''
        return super().__new__(cls, vector_str)


class FoamUniformVector(FoamVector):

    """
    Subclass of FoamVector to extract OpenFOAM uniform vector
    from basic string. If OpenFOAM uniform vector was found in input_str, the
    constructor returns string with the stripped uniform vector.
    Example: 'uniform ( 0 0 0 )'
    If uniform vector pattern was not found, the constructor returns FoamVector
    object
    """

    def __new__(cls, input_str):
        vector_str = super().__new__(cls, input_str)
        if 'uniform' in input_str and vector_str:
            return 'uniform ' + vector_str
        return vector_str


class FoamUniformScalar(FoamVector):

    """
    Subclass of FoamVector to extract OpenFOAM uniform vector
    from basic string. If OpenFOAM uniform vector was found in input_str, the
    constructor returns string with the stripped uniform vector.
    Example: 'uniform 0.0'
    If uniform vector pattern was not found, the constructor returns FoamVector
    object
    """

    def __new__(cls, input_str):
        vector_str = super().__new__(cls, input_str)
        if 'uniform' in input_str and vector_str:
            return 'uniform ' + vector_str
        return vector_str





class FoamEntry(dict):

    """
    Class subclassing from python dictionary storing a single OpenFOAM (OF)
    dictionary entry with the following keys, value pairs:
    - name: string object containing the OF variable name
    - dimensions: FoamDimensions object containing either OF dimensions set
                  string or an empty string if value is not dimensioned
    - value: string object containing either a numerical value
             or another OF-specific type
    """

    END_STMNT = ';'

    def __init__(self, *args):
        super().__init__(self)
        if not isinstance(args, str):
            if isinstance(args, (list, tuple)):
                args = ' '.join(args)
            else:
                raise TypeError('Class FoamEntry must be initialized with '
                                'either a string, list or tuple')
        args = args.strip()
        self['name'] = args.split(' ')[0]
        self['dimensions'] = FoamDimensions(args)
        value = args.split(self.END_STMNT, 1)[0].strip()
        value = value.split(' ')[-1]
        self['value'] = value

    def write(self, tab_length):
        entry_line = self['name'] + '\t\t\t'
        if self['dimensions']:
            entry_line += self['name'] + ' ' + self['dimensions']
        entry_line += self['value'] + self.END_STMNT + '\n'
        entry_line.expandtabs(tab_length)
        return entry_line

    @staticmethod
    def factory(input_str):
        input_str = FoamUniformVector(input_str)
        if input_str:
            return input_str



class FoamDict(dict):

    """
    Class storing an OpenFOAM dictionary
    as a python dictionary
    """

    DICT_OPEN = '{'
    DICT_CLOSE = '}'

    def __init__(self, *args):
        super().__init__(self)
        name, content, found_dict, rem_input = self.read(args)
        if not found_dict:
            raise ValueError('No dictionary found in provided data')
        self['name'] = name
        self['content'] = {}
        for line in content:
            entry = FoamEntry(line)
            self['content'][entry['name']] = entry

    @classmethod
    def read(cls, input_file):

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
            if open_braces == 0 and cls.DICT_OPEN in line:
                found_dict = True
                name = input_list[i - 1].strip()
                open_braces += 1
            elif open_braces > 0 and cls.DICT_OPEN in line:
                open_braces += 1
                content.append(line)
            elif open_braces > 1 and cls.DICT_OPEN in line:
                open_braces -= 1
                content.append(line)
            elif open_braces > 0:
                content.append(line)
            else:
                end_id = i
                break
        rem_list = input_list[end_id + 1:]
        return name, content, found_dict, rem_list

    def write(self, indent_space, tab_length):
        if not isinstance(indent_space, str):
            raise TypeError('indent_space must be a string of whitespaces')
        dict_lines = indent_space + self['name'] + '\n'
        dict_lines += indent_space + self.DICT_OPEN + '\n'
        for key in self['content']:
            dict_lines += indent_space + self['content'][key].write(tab_length)
        dict_lines += indent_space + self.DICT_CLOSE + '\n'
        return dict_lines


class FoamFile:

    """
    Class representing an OpenFOAM (OF) input file organized into
    header (list of strings), single entries (FoamEntry),
    and dictionaries (FoamDictionaries)
    """

    HEADER_SIZE = 15
    TAB_LENGTH = 4

    def __init__(self, input_file):
        input_list = fio.read_header(input_file)
        self.header = input_list[:self.HEADER_SIZE]
        self.body = input_list[self.HEADER_SIZE:]
        self.pure_body = [line for line in self.body if not re.search('^\s*//')]

    @staticmethod
    def read_header(input_file):

        """
        Extract the OpenFOAM header from input file

        Inputs:
            - input_file: OF-input file path or list of file lines
        Returns:
            - header: list of lines comprising the specific OF-file header
        """

        input_list = fio.convert_input_to_list(input_file)
        header = []
        for line in input_list:
            header.append(line)
            if re.search('^// *') in line:
                break
        return header

    def lookup_entry(self, name):




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
