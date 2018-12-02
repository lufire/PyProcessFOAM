#!/usr/bin/env python

import os
import re

num_pattern = '[-+]?(?:(?:\d*\.\d+)|(?:\d+\.?))(?:[Ee][+-]?\d+)?'

def replace(file_path, pattern, subst):

    """ 
    Open file, find pattern in file and replace it with substitute

    Inputs:
        - file_path: complete path of file to edit
        - pattern: string of pattern to replace 
        - subst: substitution string for the replaced pattern
    """

    with open(file_path, 'r') as f:
        file_string = f.read()

    file_string = (re.sub(pattern, subst, file_string))

    with open(file_path, 'w') as f:
        f.write(file_string)


def read_dict_from_list(in_list):

    """ 
    Extract the first and highest dictionary in hierarchy
    in OpenFOAM (OF) format from provided list 

    Inputs:
        - in_list: list of strings in OF format 
    Returns:
        - name: name of OF-dict
        - content: list of lines of the OF-dict
        - found_dict: bool to indicate whether a dictionary was found
        - rem_list: remaining list following the first dictionary
    """
    
    open_braces = 0
    found_dict = False
    content = []
    for i, line in enumerate(in_list):
        if open_braces == 0 and '{' in line:
            found_dict = True
            name = in_list[i-1].strip()
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
    rem_list = in_list[end_id+1:]

    return name, content, found_dict, rem_list 


def read_dicts_from_list(in_list):

    """ 
    Extract all OpenFOAM dictionaries in highest hierarchy
    in OpenFOAM (OF) format from list 

    Inputs:
        - file: list containing strings in OpenFOAM format
    Returns:
        - dicts: python dictionary with OF-dictionary names as keys
                 and content string list as values
    """

    dicts = {}

    found_dict = True

    while found_dict is True:
        name, content, found_dict, in_list = read_dict_from_list(in_list)
        dicts[name] = content

    return dicts


def read_dicts_from_file(file_path):

    """ 
    Extract all OpenFOAM dictionaries in highest hierarchy
    in OpenFOAM (OF) format from provided file 

    Inputs:
        - file: OpenFOAM input file 
    Returns:
        - dicts: python dictionary with OF-dictionary names as keys
                 and content string list as values
    """

    with open(file_path,'r') as f:
        lines = f.readlines()
    dicts = read_dicts_from_list(lines) 

    return dicts 


def read_boundary_conditions(field_file):

    """ 
    Extract boundary condition data from an OF field file

    Inputs:
        - bc_file: complete path of file with boundaryField
    Returns:
        - bc_patch_names: list of patch names
        - bc_patch_content: list of string list specifying 
                            each boundary condition
        - bc_patch_dict: dictionary with bc_patch names as keys and 
                         bc_patch_content as values 
    """

    dicts = read_dicts_from_file(field_file)
    bc_list = dicts['boundaryField'] 
    bc_dicts = read_dicts_from_list(bc_list)

    return bc_dicts


def read_transport_properties(tp_file):

    """ 
    Extract transport properties data from the
    OpenFOAM transportProperties file

    Inputs:
        - tp_file: complete path of OF transportProperties file 
    Returns:
        - bc_patch_names: list of patch names
        - bc_patch_content: list of string list specifying 
                            each boundary condition
        - bc_patch_dict: dictionary with bc_patch names as keys and 
                         bc_patch_content as values 
    """
        
    with open(tp_file,'r') as f:
        lines = f.readlines()
    lines = [line for line in lines if '//


        

def foam_bc_strs(foam_bc_name, value):

    boundary_name = 'outlet'
    #search_string = 'boundaryField\s*\n\s*{\s*\n'
    search_string = '\s*'+boundary_name+'\s*\n\s*{\s*\n'
    search_string += '\s*type\s*flowRateOutletVelocity\s*;\s*\n'
    search_string += '\s*volumetricFlowRate\s*'+num_pattern+'\s*;\s*\n'
    #replace_string = 'boundaryField\n{\n'
    replace_string = '\t'+boundary_name+'\n\t{\n'
    replace_string += '\t\ttype\t\t\tflowRateOutletVelocity;\n'
    replace_string += '\t\tvolumetricFlowRate\t\t\t'+str(flow_rate)+';\n'

    boundary_name = 'inlet'
    #search_string = 'boundaryField\s*\n\s*{\s*\n'
    search_string = '\s*'+boundary_name+'\s*\n\s*{\s*\n'
    search_string += '\s*type\s*fixedValue\s*;\s*\n'
    search_string += '\s*value\s*uniform\s*\(\s*('+num_pattern+'\s*)*\s*\)\s*;\s*\n'
    #replace_string = 'boundaryField\n{\n'
    replace_string = '\n\t'+boundary_name+'\n\t{\n'
    replace_string += '\t\ttype\t\t\tfixedValue;\n'
    replace_string += '\t\tvalue\t\t\tuniform ('+str(velocity_in)+' 0 0);\n'
    search_string = search_string.expandtabs(4)
    replace_string = replace_string.expandtabs(4)

    input_file = os.path.join(dir, '0.org/U')
    replace(input_file, search_string, replace_string)

    for i, ypos in enumerate(y_pos_profiles):
        search_string = 'graph\s*\n\s*{\s*\n'
        search_string += '\s*start\s*\(\s*('+num_pattern+'\s*)*\s*\)\s*;\s*\n'
        search_string += '\s*end\s*\(\s*('+num_pattern+'\s*)*\s*\)\s*;\s*\n'
        replace_string = 'graph\n{\n'
        replace_string += '\tstart\t\t('+str(np.amin(xgrid))+' '+str(ypos)+' 0);\n'
        replace_string += '\tend\t\t('+str(np.amax(xgrid))+' '+str(ypos)+' 0);\n'
        search_string = search_string.expandtabs(4)
        replace_string = replace_string.expandtabs(4)
        input_file = os.path.join(dir, 'system/singleGraph'+str(i+1))
        replace(input_file, search_string, replace_string)


    # Exchange rheology parameters
    #input_file = os.path.join(dir,'constant/transportProperties')
    #viscosity_model = 'HerschelBulkley'
    #var = params[:3]
    #var_names = ['tau0', 'k', 'n']
    #var_units = ['[0 2 -2 0 0 0 0]',
    #             '[0 2 -1 0 0 0 0]',
    #             '[0 0 0 0 0 0 0]']
    #search_params = []
    #for name in var_names:
    #    s = '\s*'+name+'\s*'+name+'\s*\[\s*([-+]?\d\s*)*\]\s*'+num_pattern+'\s*;\s*\n'
    #    search_params.append(s)

    #replace_params = []
    #for id,name in enumerate(var_names):
    #    s = '\t'+name+'\t\t\t'+name+' '+var_units[id]+' '+str(var[id])+';\n'
    #    replace_params.append(s)
    #search_string = viscosity_model+'Coeffs'+'\s*\n\s*{\s*\n'
    #for string in search_params:
    #    search_string += string
    #replace_string = viscosity_model+'Coeffs\n{\n'
    #for string in replace_params:
    #    replace_string += string
    #search_string = search_string.expandtabs(4)
    #replace_string = replace_string.expandtabs(4)
    #replace(input_file, search_string, replace_string)

    # Exchange boundary settings 
    input_file = os.path.join(dir,'0.org/U')
    type_name = 'shearStressSlipVelocity'
    var = params[:2]
    print(var)
    var_names = ['factor', 'exponent']
    search_params = ['type\s*'+type_name+'\s*;\s*\n',
                     '\s*nuName\s*nuApp\s*;\s*\n', 
                     '\s*'+var_names[0]+'\s*'+num_pattern+'\s*;\s*\n',
                     '\s*'+var_names[1]+'\s*'+num_pattern+'\s*;\s*\n']

    replace_params = ['type\t\t\tshearStressSlipVelocity;\n',
                      '\t\tnuName\t\t\tnuApp;\n',
                      '\t\t'+var_names[0]+'\t\t\t'+str(var[0])+';\n',
                      '\t\t'+var_names[1]+'\t\t'+str(var[1])+';\n']

    ## Exchange boundary settings 
    #input_file = os.path.join(dir,'0.org/U')
    #type_name = 'partialSlip'
    #var = params[3:]
    #print(var)
    #var_names = ['valueFraction']
    #search_params = ['type\s*'+type_name+'\s*;\s*\n',
    #                  '\s*'+var_names[0]+'\s*'+num_pattern+'\s*;\s*\n']

    #replace_params = ['type\t\t\t'+type_name+';\n',
    #                  '\t\t'+var_names[0]+'\t'+str(var[0])+';\n']

    search_string = (''.join(search_params)).expandtabs(4)
    replace_string = (''.join(replace_params)).expandtabs(4)
    print(replace_string)
    replace(input_file, search_string, replace_string)



runSim([0.003, 3.0])
