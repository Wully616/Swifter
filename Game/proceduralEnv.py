'''
Created on 23 Jul 2016

@author: Wully
'''
from direct.showbase.ShowBase import ShowBase
from panda3d.core import ShaderTerrainMesh, Shader, load_prc_file_data
from panda3d.core import SamplerState
 
# Required for matrix calculations
load_prc_file_data("", "gl-coordinate-system default")
 
# ...
 
terrain_node = ShaderTerrainMesh()
terrain_node.heightfield_filename = "heightfield.png"
terrain_node.target_triangle_width = 10.0
terrain_node.generate()
 
terrain_np = render.attach_new_node(terrain_node)
terrain_np.set_scale(1024, 1024, 60)
 
terrain_np.set_shader(Shader.load(Shader.SL_GLSL, "terrain.vert", "terrain.frag"))