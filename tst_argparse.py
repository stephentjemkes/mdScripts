import argparse
import random
import json

class keyvalue(argparse.Action): 
    # Constructor calling 
    def __call__( self , parser, namespace, 
                 values, option_string = None): 
        setattr(namespace, self.dest, dict()) 
          
        for value in values: 
            # split it into key and value 
            key, value = value.split('=')
            value = True if value.lower() in ['true', '1'] else False
            
            # assign into dictionary 
            getattr(namespace, self.dest)[key] = value

            
parser = argparse.ArgumentParser(description="My parser")
parser.add_argument("--my_bool", action="store_true")
parser.add_argument('-o', '--option', nargs='*', action=keyvalue,
                    help='run time options')
args = parser.parse_args()
print("{}".format(args))
option=args.option
print("{}".format(option))
print(random.randint(3, 9))
print(random.randint(300, 900))
