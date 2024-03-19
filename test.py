import os

path = "/fonts/arial.tff"
filepath = os.path.dirname(__file__)
print(path)
print(__file__, filepath)
#map_path = os.path.join(filepath, path)
map_path = filepath + path
print(map_path)
