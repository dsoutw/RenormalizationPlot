'''
Created on 2017/9/22

@author: dsou
'''
import logging

# class recordFactoryFunctionInfo(logging.LogRecord):
#     def getMessage(self):
#         print(self.args)
#         super().getMessage()
# 
# old_factory = logging.getLogRecordFactory()
# def record_factory(*args, **kwargs):
#     print(args)
#     record:logging.LogRecord = old_factory(*args, **kwargs)
#     #print(kwargs)
#     #print('before:',record.__dict__)
#     functionInfo = getattr(record,'funcionInfo',None)
#     if functionInfo is not None:
#         #record.functionInfo=' [%s]' % (functionInfo,)
#         #print(functionInfo)
#         pass
#     else:
#         record.functionInfo=''
#         pass
#     #print('after:',record.__dict__)
#     print(str(record))
#     return record
# logging.setLogRecordFactory(record_factory)

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
        msg='%s %s' % (msg,str(self.functionInfo))
#         oldFunctionInfo=self.extra.get('functionInfo',None)
#         if oldFunctionInfo is not None:
#             self.extra['functionInfo']='%s,%s' % (self.functionInfo,oldFunctionInfo)
#         else:
#             self.extra['functionInfo']='%s' % (self.functionInfo)
        return super().process(msg, kwargs)
