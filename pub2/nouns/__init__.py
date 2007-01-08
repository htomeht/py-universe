# Noun plugins loader
# The magic needs work!

# Modules in this directory should provide both interface and components.


import sys, os

plugin_path = os.path.abspath(__path__[0])
for module_file in filter(
	lambda n: n[-3:]=='.py' and n not in ('__init__.py'), 
	os.listdir(plugin_path)):
    #print "Loading %s" % module_file
    f, e = os.path.splitext(module_file)
    m  = __import__(f, globals(), locals(), [])
    for name in dir(m):
        if name[0]!='_':
            setattr(globals(), name, getattr(m, name))


