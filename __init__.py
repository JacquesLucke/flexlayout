bl_info = {
    "name": "Flexible Layout Demo",
    "description": "",
    "author": "Jacques Lucke",
    "version": (0, 0, 1),
    "blender": (2, 79, 0),
    "location": "View3D",
    "warning": "",
    "wiki_url": "",
    "category": "UI"
}

import bpy

category = "FlexLayout"

breakpoints = [0, 0, 300, 400]

class FlexLayout:
    def __init__(self):
        self.elements = []

    def render(self, layout, width):
        for element in self.elements:
            element.render(layout, width)

    def row(self, *, align = False):
        row = FlexLayoutRow(align)
        self.elements.append(row)
        return row

    def column(self, *, align = False):
        col = FlexLayoutColumn(align)
        self.elements.append(col)
        return col

    def flex(self, *, breakpoint = None, align = False):
        floatings = FlexLayoutFloatings(breakpoint, align)
        self.elements.append(floatings)
        return floatings

    def prop(self, data, attribute, *, text = "", icon = "NONE", expand = False):
        self.elements.append(FlexProp(data, attribute, text, icon, expand))

    def label(self, text):
        self.elements.append(FlexLabel(text))

    def separator(self):
        self.elements.append(FlexSeparator())

    def menu(self, idname, text):
        self.elements.append(FlexMenu(idname, text))

    def operator(self, idname, *, text = "", icon = "NONE"):
        operator = FlexOperator(idname, text, icon)
        self.elements.append(operator)
        return operator.settings

    def __repr__(self):
        return "\n".join(self.iter_repr_lines())

    def iter_repr_lines(self):
        yield type(self).__name__ + ":"
        for element in self.elements:
            if isinstance(element, FlexLayout):
                yield from ("  " + line for line in element.iter_repr_lines())
            else:
                yield "  " + type(element).__name__

class FlexLayoutRow(FlexLayout):
    def __init__(self, align):
        super().__init__()
        self.align = align

    def render(self, layout, width):
        row = layout.row(align = self.align)
        for element in self.elements:
            element.render(row, width)

class FlexLayoutColumn(FlexLayout):
    def __init__(self, align):
        super().__init__()
        self.align = align

    def render(self, layout, width):
        col = layout.column(align = self.align)
        for element in self.elements:
            element.render(col, width)

class FlexLayoutFloatings(FlexLayout):
    def __init__(self, breakpoint, align):
        super().__init__()
        self.align = align
        self.breakpoint = breakpoint

    def render(self, layout, width):
        if width <= breakpoints[self.get_breakpoint()]:
            col = layout.column(self.align)
            for element in self.elements:
                element.render(col, width)
        else:
            row = layout.column_flow(len(self.elements), self.align)
            for element in self.elements:
                element.render(row.column(self.align), width / len(self.elements))

    def get_breakpoint(self):
        if self.breakpoint is None:
            return min(len(self.elements), len(breakpoints) - 1)
        else:
            return self.breakpoint


class FlexLabel:
    def __init__(self, text):
        self.text = text

    def render(self, layout, width):
        layout.label(self.text)

class FlexProp:
    def __init__(self, data, attribute, text, icon, expand):
        self.data = data
        self.attribute = attribute
        self.text = text
        self.icon = icon
        self.expand = expand

    def render(self, layout, width):
        layout.prop(self.data, self.attribute,
            text = self.text,
            icon = self.icon,
            expand = self.expand)

class FlexSeparator:
    def render(self, layout, width):
        layout.separator()

class FlexMenu:
    def __init__(self, idname, text):
        self.idname = idname
        self.text = text

    def render(self, layout, width):
        layout.menu(self.idname, text = self.text)

class FlexOperator:
    def __init__(self, idname, text, icon):
        self.idname = idname
        self.text = text
        self.icon = icon
        self.settings = {}

    def render(self, layout, width):
        props = layout.operator(self.idname, text = self.text, icon = self.icon)
        for key, value in self.settings.items():
            setattr(props, key, value)

class FlexPanel:
    @classmethod
    def poll(cls, context):
        return cls.poll_flex(context)

    @classmethod
    def poll_flex(cls, context):
        return True

    def draw(self, context):
        flex = FlexLayout()
        self.draw_flex(context, flex)
        flex.render(self.layout, self.get_width(context))
        print(flex)

    def get_width(self, context):
        return context.region.width

class RenderPanel(FlexPanel, bpy.types.Panel):
    bl_idname = "flex_render_panel"
    bl_label = "Render"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = category
    bl_options = set()

    def draw_flex(self, context, layout):
        flex = layout.flex(align = True, breakpoint = 2)
        flex.operator("render.render", text = "Render", icon = "RENDER_STILL")
        props = flex.operator("render.render", text = "Animation", icon = "RENDER_ANIMATION")
        props["animation"] = True
        flex.operator("sound.mixdown", text = "Audio", icon = "PLAY_AUDIO")

        render = context.scene.render
        row = layout.row(align = True)
        row.prop(render, "display_mode", text = "Display")
        icon = "LOCKED" if render.use_lock_interface else "UNLOCKED"
        row.prop(render, "use_lock_interface", text = "", icon = icon)

class DimensionsPanel(FlexPanel, bpy.types.Panel):
    bl_idname = "flex_dimensions_panel"
    bl_label = "Dimensions"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = category
    bl_options = set()

    def draw_flex(self, context, layout):
        scene = context.scene
        render = scene.render

        flex = layout.flex()

        flexcol = flex.column()
        col = flexcol.column(align = True)
        col.label("Resolution")
        col.prop(render, "resolution_x", text = "X")
        col.prop(render, "resolution_y", text = "Y")
        col.prop(render, "resolution_percentage", text = "")
        col = flexcol.column(align = True)
        col.label("Aspect Ratio")
        col.prop(render, "pixel_aspect_x", text = "X")
        col.prop(render, "pixel_aspect_y", text = "Y")
        row = flexcol.row(align = True)
        row.prop(render, "use_border", text = "Border")
        row.prop(render, "use_crop_to_border", text = "Crop")

        flexcol = flex.column()
        col = flexcol.column(align = True)
        col.label("Frame Range")
        col.prop(scene, "frame_start", text = "Start Frame")
        col.prop(scene, "frame_end", text = "End Frame")
        col.prop(scene, "frame_step", text = "Frame Step")
        col = flexcol.column(align = True)
        col.label("Frame Rate")
        col.menu("RENDER_MT_framerate_presets", text = "Presets")
        col = flexcol.column(align = True)
        col.label("Time Remapping")
        row = col.row(align = True)
        row.prop(render, "frame_map_old", text = "Old")
        row.prop(render, "frame_map_new", text = "New")

class ObjectTransformsPanel(FlexPanel, bpy.types.Panel):
    bl_idname = "flex_object_transforms"
    bl_label = "Object Transforms"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = category
    bl_options = set()

    @classmethod
    def poll_flex(self, context):
        return context.active_object is not None

    def draw_flex(self, context, layout):
        object = context.active_object

        flex = layout.flex()

        col = flex.column(align = True)
        col.label("Location")
        col.prop(object, "location", text = "")

        col = flex.column(align = True)
        col.label("Rotation")
        col.prop(object, "rotation_euler", text = "")

        col = flex.column(align = True)
        col.label("Scale")
        col.prop(object, "scale", text = "")

        layout.prop(object, "rotation_mode", text = "Rotation Mode")

class PerformancePanel(FlexPanel, bpy.types.Panel):
    bl_idname = "flex_performance_panel"
    bl_label = "Performance"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = category
    bl_options = set()

    def draw_flex(self, context, layout):
        flex = layout.flex()
        render = context.scene.render

        flexcol = flex.column()
        col = flexcol.column(align = True)
        col.label("Threads")
        col.row(align = True).prop(render, "threads_mode", expand = True, text= " ")
        col.prop(render, "threads", text = "Threads")
        col = flexcol.column(align = True)
        col.label("Tile Size")
        col.prop(render, "tile_x", text = "X")
        col.prop(render, "tile_y", text = "Y")
        flexcol.prop(render, "preview_start_resolution", text = "Start Resolution")

        flexcol = flex.column()
        col = flexcol.column(align = True)
        col.label("Memory")
        col.prop(render, "use_save_buffers", text = "Save Buffers")
        col.prop(render, "use_free_image_textures", text = "Free Image Textures")
        col = flexcol.column(align = True)
        col.label("Acceleration Structure")
        col.prop(render, "raytrace_method", text = "")
        col.prop(render, "use_instances", text = "Instances")
        col.prop(render, "use_local_coords", text = "Local Coordinates")

class SearchOperator(bpy.types.Operator):
    bl_idname = "flexlayout.search"
    bl_label = "Search"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        print("hello")
        return {"FINISHED"}


panels = [
    RenderPanel,
    DimensionsPanel,
    ObjectTransformsPanel,
    PerformancePanel
]

operators = [
    SearchOperator
]

classesToRegister = panels + operators

def register():
    for panel in classesToRegister:
        bpy.utils.register_class(panel)

    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name = "3D View", space_type = "VIEW_3D")
    km.keymap_items.new("flexlayout.search", type = "F", ctrl = True, value = "PRESS")

def unregister():
    for panel in classesToRegister:
        bpy.utils.unregister_class(panel)