''' Symmetrize weights in the active group.'''

'''
*******************************************************************************
	License and Copyright
	Copyright 2012 Jordan Hueckstaedt
	This program is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

bl_info = {
	'name': 'Symmetrize Weights',
	'author': 'Jordan Hueckstaedt',
	'version': (1, 0),
	'blender': (2, 63, 0),
	'location': 'View > Weight Tools > Symmetrize',
	'warning': '', # used for warning icon and text in addons panel
	'description': 'Symmetrize weights in the selected vertex group.',
	"wiki_url": "",
	"tracker_url": "",
	"support": 'TESTING',
	'category': 'Paint'
}

import bpy

class WeightPaintSymmetrize(bpy.types.Operator):
	bl_idname = "object.weightpaint_symmetrize"
	bl_label = "Symmetrize"
	bl_options = {'REGISTER', 'UNDO'}
	
	active_index = None
	operation = bpy.props.EnumProperty(
		name = "Operation",
		items =	(('RIGHT', "Right to Left", "Right to Left"),
				('LEFT', "Left to Right", "Left to Right"),
				),
		)

	@classmethod
	def poll(cls, context):
		obj = context.active_object
		return (obj and obj.mode == 'WEIGHT_PAINT' and obj.type == 'MESH' and len(obj.vertex_groups) > 0)
	
	def restore_active_index(self, obj):
		# This is a hack.  For some reason the active vertex group changes during execution,
		if self.active_index is not None:
			obj.vertex_groups.active_index = self.active_index
	
	def execute(self, context):	
		# Get right indexes
		obj = context.object
		verts = obj.data.vertices
		
		if self.active_index is None:
			self.active_index = context.active_object.vertex_groups.active_index
		
		if self.operation == 'RIGHT':
			other_indexes = [vert.index for vert in verts if vert.co[0] < 0]
		else:
			other_indexes = [vert.index for vert in verts if vert.co[0] > 0]
		
		# Flip weights (Mirror operator also handles masking for free)
		self.restore_active_index( obj )
		bpy.ops.object.vertex_group_mirror(flip_group_names = False)
		
		# Save flipped weights
		weights = {}
		for i in other_indexes:
			for x, group in enumerate(obj.data.vertices[i].groups):
				if group.group == self.active_index:
					weights[i] = (x, group.weight)
					break
		
		# Restore weights
		self.restore_active_index( obj )
		bpy.ops.object.vertex_group_mirror(flip_group_names = False)

		# Apply flipped weights
		for x, i in enumerate(other_indexes):
			if i in weights:
				obj.data.vertices[i].groups[weights[i][0]].weight = weights[i][1]
		
		obj.data.update()
		
		self.restore_active_index( obj )
		return{'FINISHED'} 
	
	def invoke(self, context, event):
		self.active_index = context.active_object.vertex_groups.active_index
		self.operation = context.scene.weightpaint_symmetrize_operation
		return self.execute(context)

def panel_func(self, context):	
	row = self.layout.row(align = True)
	row.alignment = 'EXPAND'
	row.operator("object.weightpaint_symmetrize")
	

def register():
	bpy.utils.register_module(__name__)
	bpy.types.VIEW3D_PT_tools_weightpaint.append(panel_func)
	
	bpy.types.Scene.weightpaint_symmetrize_operation = bpy.props.EnumProperty(
		name = "Operation",
		items =	(('RIGHT', "Right to Left", "Right to Left"),
				('LEFT', "Left to Right", "Left to Right"),
				),
		)
	
def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.VIEW3D_PT_tools_weightpaint.remove(panel_func)
	del bpy.types.Scene.weightpaint_symmetrize_operation
	
if __name__ == "__main__":
	register()
