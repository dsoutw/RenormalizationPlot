'''
Renormalization Plot - lib/module.py
    Utilities for load modules dynamically

Copyright (C) 2017 Dyi-Shing Ou. All Rights Reserved.
'''

import importlib.util
import os.path

def loadFile(path, name=None):
    '''
    Load function from a python file
    
    Supported file format:
        .py:    python file
    
    Supported function:
        unimodal maps (one parameter family)
    
    @param path: Path of the file
    @type path: str
    @param param: Name of the module. Default is set to be the file name
    @type param: str 
    '''
    
    if name is None:
        name=os.path.basename(path)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module