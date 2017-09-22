'''
Created on 2017/9/22

@author: dsou
'''
import logging

old_factory = logging.getLogRecordFactory()
def record_factory(*args, **kwargs):
    record = old_factory(*args, **kwargs)
    functionInfo = getattr(record,"funcionInfo",None)
    if functionInfo is not None:
        record.functionInfo=' [%s]' % (functionInfo,)
    else:
        record.functionInfo=''
    return record
logging.setLogRecordFactory(record_factory)

class appendFunctionInfoAdapter(logging.LoggerAdapter):
    """
    This example adapter expects the passed in dict-like object to have a
    'connid' key, whose value in brackets is prepended to the log message.
    """
    functionInfo=""
    def __init__(self, logger, functionInfo:str=''):
        self.functionInfo=functionInfo
        super().__init__(logger, {})
        
    def process(self, msg, kwargs:dict):
        oldFunctionInfo=kwargs.get('functionInfo',None)
        if oldFunctionInfo is not None:
            kwargs['functionInfo']='%s,%s' % (self.functionInfo,oldFunctionInfo)
        return msg, kwargs