#!/usr/bin/env python
'''
This script scans the RDTool .xml scripts inside a directory and creates a main MODELNAME.xml script
that contains calls to every MODELNAME.Test.xxx.xml found in the same directory.
This is supposed to be a feature from TMX ('Sets' feature) but it generates broken xml files.
'''
import argparse
import pprint
import os
import sys
import platform

def load_header(path_to_header_file):
    '''
    Loads header file and return as string
    Args:
        path_to_header_file (str): path to header file
    Return:
        header (str): header file content as string
    '''
    try:
        header_file = open(path_to_header_file, 'r')
        header = header_file.read()
        return header
    except IOError as error:
        print("Couldn't read header file \n(%s)." %error)
        raise

def load_footer(path_to_footer_file):
    '''
    Loads footer file and return as string
    Args:
        path_to_footer_file (str): path to footer file
    Return:
        footer (str): footer file content as string
    '''
    try:
        footer_file = open(path_to_footer_file, 'r')
        footer = footer_file.read()
        return footer
    except IOError as error:
        print("Couldn't read footer file (%s)." %error)
        print(error)
        raise

def scan_for_models(script_folder_path):
    '''
    Scans script_folder_path for model names. The scripts must follow the MODEL_NAME.Test.xxx.xml
    naming convention where xxx is any 3-digit zero-padded integer

    Args:
        script_folder_path (str): Path to folder where test scripts xml files are located.

    Returns:
        models (dict): Dictionary whose keys are models names and values are tests counted.
    '''
    try:
        filenames = os.listdir(script_folder_path)
    except OSError as error:
        print("Error scaning origin directory!")
        print(error)
        raise
    models = {}
    for filename in filenames:
        if '.Test.' in filename:
            model_name = filename.split('.Test.')[0]
            if model_name not in models:
                models[model_name] = 1
            else:
                models[model_name] = models[model_name] + 1
    return models

def create_main_string(model_name, tests_count, header, footer):
    '''
    Creates the content of a MODELNAME.xml script with header and footer based on templates and
    containing calls to every test script found with the same MODELNAME, counted using tests_count.

    Args:
        model_name (str): String that represent the model name
        e.g XFS_SPNAME_COMMAND_SUCCESS

        tests_count (int): Number of tests scripts found for the same model

        header (str): Header template used to generate the MODELNAME.xml

        footer (str): Footer template used to generate the MODELNAME.xml

    Returns:
        main_string (str): A string representing the MODELNAME.xml file, yet not created.
    '''

    main_string = header
    for i in range(1, tests_count + 1):
        main_string += "<INCLUDE FileName=\"" + model_name + ".Test."+ format(i, '03d') +  \
        ".xml\" " + "NameSpace=\"\" TAB=\"10\" LineComment=\"0\"/>" + "\n"
    main_string += footer
    return main_string

def create_main_file(model_name, main_string, destination_folder):
    '''
    Creates a file model_name.xml containing main_string

    Args:
        model_name (str): String that represent the model name

        main_string (str): A string representing the MODELNAME.xml file, yet not created.

        destination_folder (str): destination folder path

    Returns:
        int 0 for success
        int 1 for failure
    '''
    file_name = model_name + ".xml"
    if destination_folder.endswith("\\") is False:
        destination_folder += "\\"
    dest = destination_folder + file_name
    try:
        with open(dest, 'w+') as file:
            file.write(main_string)
            return 0
    except IOError as error:
        print("Couldn't open or write to file (%s)." %error)
        raise

def main():
    '''
    main function. gets args from command line and produces model_name.xml files
    using functions defined in main_script_creator.py
    '''
    if platform.system() != 'Windows':
        print("This script only runs properly on Windows.\n")
        sys.exit(1)

    parser = argparse.ArgumentParser()

    parser.add_argument("origin_folder", \
    help="the directory where the test case scripts are located")

    parser.add_argument("destination_folder", \
    help="the directory where test set scripts will be saved")

    parser.add_argument("path_to_header", \
    help="the path to header template file")

    parser.add_argument("path_to_footer", \
    help="the path to footer template file")

    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")

    args = parser.parse_args()
    if args.verbose:
        print("\nVerbosity turned on!\n")

    try:
        header = load_header(args.path_to_header)
    except IOError:
        sys.exit(1)
    if args.verbose:
        print("Header successfully loaded!\n")

    try:
        footer = load_footer(args.path_to_footer)
    except IOError:
        sys.exit(1)
    if args.verbose:
        print("Footer successfully loaded!\n")

    try:
        models = scan_for_models(args.origin_folder)
    except OSError:
        sys.exit(1)

    if args.verbose:
        print("The folliwng models detected are shown as: {\'model_name\': test_count}\n")
        pprint.pprint(models)
        print()

    for model_name, test_count in models.items():
        main_string = create_main_string(model_name, test_count, header, footer)
        try:
            create_main_file(model_name, main_string, args.destination_folder)
        except IOError:
            sys.exit(1)
    if args.verbose:
        print("Created model_name.xml files successfully!")

    sys.exit(0)

if __name__ == "__main__":
    main()

__author__ = "Douglas Navarro"
__version__ = "1.0"
__status__ = "Development"