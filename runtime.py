import os
import random

class RuntimeFunctions:
    @staticmethod
    def function_readln():
        inputs = input().split()
        inputs.append('')
        return [{index: [x, 'string'] for (index, x) in enumerate(inputs)}, 'array']
    
    @staticmethod
    def function_floatval(literal):
        return [float(literal[0]), 'float']
    
    @staticmethod
    def function_cmd(cmd):
        os.system(cmd[0])

    @staticmethod
    def function_rand(min, max):
        return [random.randint(min[0], max[0]), 'int']

RuntimeFunctions.function_readln.vparams = ()
RuntimeFunctions.function_floatval.vparams = ('literal', )
RuntimeFunctions.function_cmd.vparams = ('cmd', )
RuntimeFunctions.function_rand.vparams = ('min', 'max')
