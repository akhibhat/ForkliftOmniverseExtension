"""
| File: ui_window.py
| Author: Akhilesh Bhat
| Description: Definition of WidgetWindow which contains all the UI code that defines the extension GUI
"""

__all__ = ["WidgetWindow"]

# External packages
import numpy as np 

# Omniverse general API
import carb
import omni.ui as ui
from omni.ui import color as cl 

from .ui_backend import UIBackend
from Forklift_Simulator_python.global_variables import ROBOTS, SIMULATION_ENVIRONMENTS, WINDOW_TITLE

class WidgetWindow(ui.Window):
    # Design constants for the widgets
    LABEL_PADDING = 120
    BUTTON_HEIGHT = 50
    GENERAL_SPACING = 5

    WINDOW_WIDTH = 300
    WINDOW_HEIGHT = 850

    BUTTON_SELECTED_STYLE = {
        "Button": {
            "background_color": 0xFF5555AA,
            "border_color": 0xFF5555AA,
            "border_width": 2,
            "border_radius": 5,
            "padding": 5,
        }
    }

    BUTTON_BASE_STYLE = {
        "Button": {
            "background_color": cl("#292929"),
            "border_color": cl("#292929"),
            "border_width": 2,
            "border_radius": 5,
            "padding": 5,
        }
    }

    def __init__(self, backend: UIBackend, **kwargs):
        """
        Constructor for the Window UI widget of the extension. Receives as input a UIBackend
        that implements all the callbacks to handle button clicks, drop-down menu actions, 
        etc. (abstracting the interface between the logic of the code and the ui)
        """
        # Setup the base widget window
        super().__init__(
            WINDOW_TITLE, width=WidgetWindow.WINDOW_WIDTH, height=WidgetWindow.WINDOW_HEIGHT, visible=True, **kwargs
        )
        self.deferred_dock_in("Property", ui.DockPolicy.CURRENT_WINDOW_IS_ACTIVE)

        # Setup the backend that will be the bridge between the logic and the UI
        self._backend = backend

        # Bind the UI Backend to this window
        self._backend.set_window_bind(self)

        # Auxiliary attributes for getting the transforms of the vehicle from the UI
        self._vehicle_transform_models = []

        # Build the actual window UI
        self._build_window()

    def destroy(self):

        # Clear the world and the stage correctly
        self._backend.on_clear_scene()

        # Destroy all children
        super().destroy()

    def _build_window(self):

        # Define the UI of the widget window
        with self.frame:

            # Vertical stack of menus
            with ui.VStack():

                # Create a frame for selecting which scene to load
                self._scene_selection_frame()
                ui.Spacer(height=5)

                # Create a frame for selecting which robot to load
                self._robot_selection_frame()
                ui.Spacer()

    def _scene_selection_frame(self):
        """
        Method that implements a dropdown menu with the list of available simulation
        environments for the vehicle
        """

        # Frame for selecting the simulation environment to load
        with ui.CollapsableFrame("Scene Selection"):
            with ui.VStack(height=0, spacing=10, name='frame_v_stack'):
                ui.Spacer(height=WidgetWindow.GENERAL_SPACING)

                # Iterate over all existing pre-made worlds bundled with this extension
                with ui.HStack():
                    ui.Label("World Assets", width=WidgetWindow.LABEL_PADDING, height=10.0)

                    # Combo box with the available environments to select from
                    dropdown_menu = ui.ComboBox(0, height=10, name="environments")
                    for environment in SIMULATION_ENVIRONMENTS:
                        dropdown_menu.model.append_child_item(None, ui.SimpleStringModel(environment))

                    # Allow the backend to know which option was selected in the dropdown menu
                    self._backend.set_scene_dropdown(dropdown_menu.model)

                ui.Spacer(height=0)

                with ui.HStack():
                    with ui.VStack():
                        # Button for loading the desired scene
                        ui.Button(
                            "Load Scene",
                            height=WidgetWindow.BUTTON_HEIGHT,
                            clicked_fn=self._backend.on_load_scene,
                            style=WidgetWindow.BUTTON_BASE_STYLE,
                        )

                        # Button to reset the stage
                        ui.Button(
                            "Clear Scene",
                            height=WidgetWindow.BUTTON_HEIGHT,
                            clicked_fn=self._backend.on_clear_scene,
                            style=WidgetWindow.BUTTON_BASE_STYLE,
                        )

    def _robot_selection_frame(self):
        """
        Method that implements a frame that allows the user to choose which robot that is 
        about to be spawned
        """

        # Auxiliary function to handle the "switch behavior of the buttons that
        # are used to choose between ROS or keyboard or joystick controls
        def handle_ros_keyboard_joystick_switch(self, ros_button, keyboard_button, joystick_button, button):

            # Handle the UI of both buttons switching off and on
            if button == "ros":
                ros_button.enabled = False
                keyboard_button.enabled = True
                joystick_button.enabled = True
                ros_button.set_style(WidgetWindow.BUTTON_SELECTED_STYLE)
                keyboard_button.set_style(WidgetWindow.BUTTON_BASE_STYLE)
                joystick_button.set_style(WidgetWindow.BUTTON_BASE_STYLE)

            elif button == "keyboard":
                ros_button.enabled = True
                keyboard_button.enabled = False
                joystick_button.enabled = True
                ros_button.set_style(WidgetWindow.BUTTON_BASE_STYLE)
                keyboard_button.set_style(WidgetWindow.BUTTON_SELECTED_STYLE)
                joystick_button.set_style(WidgetWindow.BUTTON_BASE_STYLE)

            elif button == "joystick":
                ros_button.enabled = True
                keyboard_button.enabled = True
                joystick_button.enabled = False
                ros_button.set_style(WidgetWindow.BUTTON_BASE_STYLE)
                keyboard_button.set_style(WidgetWindow.BUTTON_BASE_STYLE)
                joystick_button.set_style(WidgetWindow.BUTTON_SELECTED_STYLE)

            self._backend.set_streaming_backend(button)

        # --------------------------
        # Function UI starts here
        # --------------------------

        # Frame for selecting the vehicle to load 
        with ui.CollapsableFrame(title="Vehicle Selection"):
            with ui.VStack(height=0, spacing=10, name="frame_v_stack"):
                ui.Spacer(height=WidgetWindow.GENERAL_SPACING)

                # Iterate over all existing robots in the extension
                with ui.HStack():
                    ui.Label("Vehicle Model", name="label", width=WidgetWindow.LABEL_PADDING)

                    # Combo box with the available vehicles to select from
                    dropdown_menu = ui.ComboBox(0, height=10, name="robots")
                    for robot in ROBOTS:
                        dropdown_menu.model.append_child_item(None, ui.SimpleStringModel(robot))
                    self._backend.set_vehicle_dropdown(dropdown_menu.model)

                with ui.HStack():
                    ui.Label("Vehicle ID", name='label', width=WidgetWindow.LABEL_PADDING)
                    vehicle_id_field = ui.IntField()
                    self._backend.set_vehicle_id_field(vehicle_id_field.model)

                self._transform_frame()

                ui.Label("Control Input Backend")

                with ui.HStack():
                    with ui.VStack():
                        # Buttons that behave like switches to choose which network
                        # interface to control the vehicle
                        ros_button = ui.Button(
                            "ROS",
                            height=WidgetWindow.BUTTON_HEIGHT,
                            style=WidgetWindow.BUTTON_BASE_STYLE,
                            enabled=False,
                        )

                        keyboard_button = ui.Button(
                            "Keyboard",
                            height=WidgetWindow.BUTTON_HEIGHT,
                            style=WidgetWindow.BUTTON_BASE_STYLE,
                            enabled=True,
                            visible=False
                        )

                        joystick_button = ui.Button(
                            "Joystick",
                            height=WidgetWindow.BUTTON_HEIGHT,
                            style=WidgetWindow.BUTTON_BASE_STYLE,
                            enabled=False
                        )

                        ros_button.set_clicked_fn(lambda: handle_ros_keyboard_joystick_switch(self, ros_button, keyboard_button, joystick_button, "ros"))
                        keyboard_button.set_clicked_fn(lambda: handle_ros_keyboard_joystick_switch(self, ros_button, keyboard_button, joystick_button, "keyboard"))
                        joystick_button.set_clicked_fn(lambda: handle_ros_keyboard_joystick_switch(self, ros_button, keyboard_button, joystick_button, "joystick"))

                self._mode_selection_frame()

                # Button to load the vehicle
                ui.Button(
                    "Load Vehicle",
                    height=WidgetWindow.BUTTON_HEIGHT,
                    clicked_fn=self._backend.on_load_vehicle,
                    style=WidgetWindow.BUTTON_BASE_STYLE,
                )

    def _transform_frame(self):
        """
        Method that implements a transform frame to translate and rotate an object
        that is about to be spawned
        """

        components = ['Position', 'Rotation']
        all_axis = ['X', 'Y', 'Z']
        colors = {'X': 0xFF5555AA, "Y": 0xFF76A371, "Z": 0xFFA07D4F}
        default_values = [0.0, 0.0, 0.1]

        with ui.CollapsableFrame("Position and Orientation"):
            with ui.VStack(spacing=8):

                ui.Spacer(height=0)

                # Iterate over the position and rotation menus
                for component in components:
                    with ui.HStack():
                        with ui.HStack():
                            ui.Label(component, name='transform', width=50)
                            ui.Spacer()

                        # Fields X, Y and Z
                        for axis, default_value in zip(all_axis, default_values):
                            with ui.HStack():
                                with ui.ZStack(width=15):
                                    ui.Rectangle(
                                        width=15,
                                        height=20,
                                        style={
                                            'background_color': colors[axis],
                                            'border_radius': 3,
                                            'corner_flag': ui.CornerFlag.LEFT,
                                        },
                                    )
                                    ui.Label(axis, name='transform_label', alignment=ui.Alignment.CENTER)
                                if component == 'Position':
                                    float_drag = ui.FloatDrag(name='transform', min=-1000000, max=1000000, step=0.01)
                                    float_drag.model.set_value(default_value)
                                else:
                                    float_drag = ui.FloatDrag(name='transform', min=-180.0, max=180.0, step=1.0)

                                # Save the model of each FloatDrag such that we can access its values later on
                                self._vehicle_transform_models.append(float_drag.model)
                                ui.Circle(name='transform', width=20, radius=3.5, size_policy=ui.CircleSizePolicy.FIXED)
                ui.Spacer(height=0)

    def _fork_manipulation_frame(self):
        """
        Method that helps manipulate the forks on the forklift
        """

        components = ["Shift/Reach", "Rotate/Tilt", "Lift"]
        all_axis = ["X", "Y", "Z"]
        colors = {'X': 0xFF5555AA, "Y": 0xFF76A371, "Z": 0xFFA07D4F}
        default_values = [0.0, 0.0, 0.1]

    def _mode_selection_frame(self):

        with ui.CollapsableFrame("Mode Selection"):
            with ui.VStack(height=0, spacing=10, name="frame_v_stack"):
                ui.Spacer(height=WidgetWindow.GENERAL_SPACING)

                # Iterate over all existing robots in the extension
                with ui.HStack():
                    ui.Label("Extension Mode", name="label", width=WidgetWindow.LABEL_PADDING)

                    # Combo box with the available vehicles to select from
                    mode_dropdown_menu = ui.ComboBox(0, height=10, name="mode")
                    mode_dropdown_menu.model.append_child_item(None, ui.SimpleStringModel("Digital Twin"))
                    mode_dropdown_menu.model.append_child_item(None, ui.SimpleStringModel("Simulation"))
                
                    self._backend.set_mode_field(mode_dropdown_menu.model)

    def get_selected_vehicle_attitude(self):
        # Extract the vehicle desired position and orientation for spawning
        if len(self._vehicle_transform_models) == 6:
            vehicle_pos = np.array([self._vehicle_transform_models[i].get_value_as_float() for i in range(3)])
            vehicle_orientation = np.array(
                [self._vehicle_transform_models[i].get_value_as_float() for i in range(3, 6)]
            )

            return vehicle_pos, vehicle_orientation
        
        return None, None
    
    def _action_graph_components_frame(self):
        """
        Method that implements a frame that allows the user to choose which components need
        to be added in the action graph
        """