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

class FlexLayout:
    def __init__(self):
        self.groups = []

    def group(self):
        group = FlexGroup()
        self.groups.append(group)
        return group

    def render(self, layout, width):
        col_amount = width // 300 + 1
        for i, group in enumerate(self.groups):
            if i % col_amount == 0:
                row = layout.row()
            group.render(row, width / col_amount)

class FlexGroup:
    def __init__(self):
        self.elements = []

    def column(self):
        col = FlexColumn()
        self.elements.append(col)
        return col

    def render(self, layout, width):
        for element in self.elements:
            element.render(layout, width)

class FlexColumn:
    def __init__(self):
        self.elements = []

    def label(self, text):
        self.elements.append(FlexLabel(text))

    def prop(self, data, attribute, text):
        self.elements.append(FlexProp(data, attribute, text))

    def render(self, layout, width):
        col = layout.column()
        for element in self.elements:
            element.render(col, width)

class FlexLabel:
    def __init__(self, text):
        self.text = text

    def render(self, layout, width):
        layout.label(self.text)

class FlexProp:
    def __init__(self, data, attribute, text):
        self.data = data
        self.attribute = attribute
        self.text = text

    def render(self, layout, width):
        layout.prop(self.data, self.attribute, text = self.text)

class FlexPanel:
    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        flex = FlexLayout()
        self.draw_flex(context, flex)
        flex.render(self.layout, self.get_width(context))

    def get_width(self, context):
        return context.region.width

class DimensionsPanel(FlexPanel, bpy.types.Panel):
    bl_idname = "flex_dimensions_panel"
    bl_label = "Dimensions"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = category
    bl_options = set()

    def draw_flex(self, context, flex):
        scene = context.scene
        render = scene.render

        group = flex.group()
        col = group.column()
        col.label("Resolution")
        col.prop(render, "resolution_x", "X")
        col.prop(render, "resolution_y", "Y")
        col.prop(render, "resolution_percentage", "")

        group = flex.group()
        col = group.column()
        col.label("Frame Rate")
        col.prop(scene, "frame_start", "Start Frame")
        col.prop(scene, "frame_end", "End Frame")
        col.prop(scene, "frame_step", "Frame Step")


panels = [
    DimensionsPanel
]

def register():
    for panel in panels:
        bpy.utils.register_class(panel)

def unregister():
    for panel in panels:
        bpy.utils.unregister_class(panel)