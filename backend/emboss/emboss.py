import bpy
import bmesh
import mathutils
import math
from math import radians
from math import *
from mathutils import Vector
import addon_utils

# Enable necessary plugins
bpy.ops.preferences.addon_enable(module="io_import_images_as_planes")
# addon_utils.enable("io_import_images_as_planes")

class SetFirstPoints():
    bl_idname = "curvetools.set_first_points"
    bl_label = "Set first points"
    bl_description = "Set the selected points as the first point of each spline"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, curve):
        splines_to_invert = []

#        curve = bpy.context.object

        bpy.ops.object.mode_set('INVOKE_REGION_WIN', mode='EDIT')

        # Check non-cyclic splines to invert
        for i in range(len(curve.data.splines)):
            b_points = curve.data.splines[i].bezier_points

            if i not in self.cyclic_splines:  # Only for non-cyclic splines
                if b_points[len(b_points) - 1].select_control_point:
                    splines_to_invert.append(i)

        # Reorder points of cyclic splines, and set all handles to "Automatic"

        # Check first selected point
        cyclic_splines_new_first_pt = {}
        for i in self.cyclic_splines:
            sp = curve.data.splines[i]

            for t in range(len(sp.bezier_points)):
                bp = sp.bezier_points[t]
                if bp.select_control_point or bp.select_right_handle or bp.select_left_handle:
                    cyclic_splines_new_first_pt[i] = t
                    break  # To take only one if there are more

        # Reorder
        for spline_idx in cyclic_splines_new_first_pt:
            sp = curve.data.splines[spline_idx]

            spline_old_coords = []
            for bp_old in sp.bezier_points:
                coords = (bp_old.co[0], bp_old.co[1], bp_old.co[2])

                left_handle_type = str(bp_old.handle_left_type)
                left_handle_length = float(bp_old.handle_left.length)
                left_handle_xyz = (
                        float(bp_old.handle_left.x),
                        float(bp_old.handle_left.y),
                        float(bp_old.handle_left.z)
                        )
                right_handle_type = str(bp_old.handle_right_type)
                right_handle_length = float(bp_old.handle_right.length)
                right_handle_xyz = (
                        float(bp_old.handle_right.x),
                        float(bp_old.handle_right.y),
                        float(bp_old.handle_right.z)
                        )
                spline_old_coords.append(
                        [coords, left_handle_type,
                        right_handle_type, left_handle_length,
                        right_handle_length, left_handle_xyz,
                        right_handle_xyz]
                        )

            for t in range(len(sp.bezier_points)):
                bp = sp.bezier_points

                if t + cyclic_splines_new_first_pt[spline_idx] + 1 <= len(bp) - 1:
                    new_index = t + cyclic_splines_new_first_pt[spline_idx] + 1
                else:
                    new_index = t + cyclic_splines_new_first_pt[spline_idx] + 1 - len(bp)

                bp[t].co = Vector(spline_old_coords[new_index][0])

                bp[t].handle_left.length = spline_old_coords[new_index][3]
                bp[t].handle_right.length = spline_old_coords[new_index][4]

                bp[t].handle_left_type = "FREE"
                bp[t].handle_right_type = "FREE"

                bp[t].handle_left.x = spline_old_coords[new_index][5][0]
                bp[t].handle_left.y = spline_old_coords[new_index][5][1]
                bp[t].handle_left.z = spline_old_coords[new_index][5][2]

                bp[t].handle_right.x = spline_old_coords[new_index][6][0]
                bp[t].handle_right.y = spline_old_coords[new_index][6][1]
                bp[t].handle_right.z = spline_old_coords[new_index][6][2]

                bp[t].handle_left_type = spline_old_coords[new_index][1]
                bp[t].handle_right_type = spline_old_coords[new_index][2]

        # Invert the non-cyclic splines designated above
        for i in range(len(splines_to_invert)):
            bpy.ops.curve.select_all('INVOKE_REGION_WIN', action='DESELECT')

            bpy.ops.object.editmode_toggle('INVOKE_REGION_WIN')
            curve.data.splines[splines_to_invert[i]].bezier_points[0].select_control_point = True
            bpy.ops.object.editmode_toggle('INVOKE_REGION_WIN')

            bpy.ops.curve.switch_direction()

        bpy.ops.curve.select_all('INVOKE_REGION_WIN', action='DESELECT')

        # Keep selected the first vert of each spline
        bpy.ops.object.editmode_toggle('INVOKE_REGION_WIN')
        for i in range(len(curve.data.splines)):
            if not curve.data.splines[i].use_cyclic_u:
                bp = curve.data.splines[i].bezier_points[0]
            else:
                bp = curve.data.splines[i].bezier_points[
                                                        len(curve.data.splines[i].bezier_points) - 1
                                                        ]

            bp.select_control_point = True
            bp.select_right_handle = True
            bp.select_left_handle = True

        bpy.ops.object.editmode_toggle('INVOKE_REGION_WIN')

        return {'FINISHED'}

    def invoke(self, curve):
#        curve = bpy.context.object

        # Check if all curves are Bezier, and detect which ones are cyclic
        self.cyclic_splines = []
        for i in range(len(curve.data.splines)):
            if curve.data.splines[i].type != "BEZIER":
                self.report({'WARNING'}, "All splines must be Bezier type")

                return {'CANCELLED'}
            else:
                if curve.data.splines[i].use_cyclic_u:
                    self.cyclic_splines.append(i)

        self.execute(curve)

        return {'FINISHED'}


def select_edge(obj):
    """Selects the closest edge to the cursor on the target object and separates it into a new object."""
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.curve.select_all(action='SELECT')
    bpy.ops.curve.spline_type_set(type='BEZIER')
    bpy.ops.curve.select_all(action='DESELECT')
    _data = obj.data
    bezier_points = []
    for spline in _data.splines:
        for point in spline.bezier_points:
            bezier_points.append(point)

    v1= bpy.context.scene.cursor.location
    wmtx = obj.matrix_world
    print(v1)
    print(wmtx)
    v2 = ""
    v2 = bezier_points[0]
    min = round(math.sqrt(math.fabs((((((v1[0])-(v2.co.x))**2))+((((v1[1])-(v2.co.y))**2))+((((v1[2])-(v2.co.z))**2))))),6)
    near_point = v2

    for v2 in bezier_points:
        v2.select_control_point = False
        conv_v2 = wmtx @ v2.co
        distance = round(math.sqrt(math.fabs((((((v1[0])-(conv_v2[0]))**2))+((((v1[1])-(conv_v2[1]))**2))+((((v1[2])-(conv_v2[2]))**2))))),6)
        if min > distance:
            min = distance
            near_point = v2
            
    near_point.select_control_point = True
    bpy.ops.curve.select_linked()
    bpy.ops.curve.select_all(action='INVERT')
    bpy.ops.curve.delete(type='VERT')
    
    near_point.select_control_point = True
    set_first_point = SetFirstPoints()
    set_first_point.invoke(obj)

    bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.ops.object.select_all(action = 'DESELECT')
    
    return obj
    
    
def create_obj(file_name, file_path, scale_X, scale_Y):
    """Imports an image as a plane, subdivides it, and applies a displacement modifier to create an embossed effect."""
    # Import the image as a plane
    bpy.ops.import_image.to_plane(shader='SHADELESS', files=[{'name':file_path + file_name}])
    image_plane = bpy.context.selected_objects[0]
    
    # Subdivide the plane for more detail
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide(number_cuts=3000)
    bpy.ops.object.mode_set(mode="OBJECT")
    ob = bpy.context.active_object
    
    # Apply displacement modifier
    tex = bpy.data.textures.new(name="Tex_Altura", type="IMAGE")
    img = bpy.data.images.load(file_path + file_name)
    tex.image = img
    tex.extension = 'EXTEND'

    mod = ob.modifiers.new("", 'DISPLACE')
    mod.strength = 0.04
    mod.mid_level = 0
    mod.texture_coords = 'UV'
    mod.texture = tex
    bpy.ops.texture.new()
    bpy.ops.image.open(filepath=file_path + file_name, directory=file_path, files=[{"name":file_name, "name":file_name}], show_multiview=False)
    bpy.context.object.modifiers["Displace"].strength = -0.05
    bpy.context.object.modifiers["Displace"].mid_level = 1
    bpy.ops.object.modifier_apply(modifier="Displace")
    bpy.ops.object.modifier_add(type='SUBSURF')
    bpy.ops.object.mode_set(mode='OBJECT')
    ob.select_set(True)
    
    pattern_obj = bpy.context.selected_objects[0]
    pattern_obj.scale = (scale_X, scale_Y, 1)


# Main script to emboss a pattern onto a 3D model and export it
obj_path = '/home/code/Documents/Projects/patternToModel/source/cylinder.glb'
file_path = '/home/code/Documents/Projects/patternToModel/source/'
file_name = 'pattern.png'


bpy.ops.object.delete()
# Import the 3D model
bpy.ops.import_scene.gltf(filepath=obj_path)
imported_objects = [obj for obj in bpy.context.selected_objects]
obj = bpy.data.objects[imported_objects[0].name]

# Create the embossed object from the pattern image
create_obj(file_name = file_name, file_path = file_path, scale_X = 1, scale_Y = 1)
imported_objects = [obj for obj in bpy.context.selected_objects]
text = bpy.data.objects[imported_objects[0].name]
text.select_set(True)

# Position and modify the embossed object
bpy.context.view_layer.objects.active = text
text.rotation_mode = 'XYZ'
bpy.context.scene.cursor.location = (1.8897, 1.8525, 4.2349)
cursor_location = bpy.context.scene.cursor.location
text.location = cursor_location
location_Y = text.location.y
text.rotation_euler = (radians(234), radians(90), radians(0))

print(cursor_location)

# Make plane
bpy.ops.mesh.primitive_plane_add(enter_editmode=False, align='WORLD', location=cursor_location, scale=(1, 1, 1))
imported_objects = [obj for obj in bpy.context.selected_objects]
plane_obj = bpy.data.objects[imported_objects[0].name]
plane_obj.scale = (50, 50, 50)
new_mod = plane_obj.modifiers.new(type='BOOLEAN', name="boolean")
new_mod.operation = 'INTERSECT'
new_mod.object = obj
bpy.ops.object.modifier_apply(modifier=new_mod.name)

# # Apply boolean operation to merge embossed pattern with the model
bpy.context.view_layer.objects.active = plane_obj
bpy.ops.object.convert(target='CURVE')
new_plan_obj = select_edge(plane_obj)
bpy.ops.object.select_all(action='DESELECT')
new_plan_obj.select_set(True)

text.select_set(True)
new_plan_obj.select_set(False)
curve_mod = text.modifiers.new(type='CURVE', name="Curve")
curve_mod.object = new_plan_obj
text.rotation_euler = (radians(90), radians(90), radians(0))
bpy.context.view_layer.objects.active = text

bpy.ops.object.modifier_apply(modifier="Subdivision")
bpy.ops.object.modifier_apply(modifier="Curve")
bpy.ops.object.select_all(action='DESELECT')
text.select_set(True)


boolean_mod = text.modifiers.new(type='BOOLEAN', name="boolean")
boolean_mod.operation = 'UNION'
boolean_mod.object = obj
bpy.ops.object.modifier_apply(modifier="boolean")
bpy.ops.object.select_all(action='DESELECT')
obj.select_set(True)
bpy.ops.object.delete()
new_plan_obj.select_set(True)
bpy.ops.object.delete()
text.select_set(True)

## Export the modified model
export_path = "/home/code/Documents/Projects/patternToModel/source/new_cylinder.glb"
bpy.ops.export_scene.gltf(filepath=export_path, use_selection=True)