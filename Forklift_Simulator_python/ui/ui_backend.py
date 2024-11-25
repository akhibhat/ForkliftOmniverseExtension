"""
| File: ui_backend.py
| Author: Akhilesh Bhat
| Description: Definition of the UiBackend which is an abstraction layer betweeen 
                 the extension UI and code logic features
"""

# External packages
import os
import asyncio
from scipy.spatial.transform import Rotation

# Omniverse extensions
import carb
import omni.ui as ui

# Sim Extension configurations
from Forklift_Simulator_python.global_variables import ROBOTS, SIMULATION_ENVIRONMENTS
from Forklift_Simulator_python.logic.interface.simulation_interface import SimInterface

# Vehicle Manager to spawn vehicles
# from Forklift_Simulator_python.logic.vehicle_manager import VehicleManager
# from Forklift_Simulator_python.logic.vehicles.single_rear_wheel_forklift import SingleRearWheelForklift
# from Forklift_Simulator_python.logic.vehicles.vehicle_configs import SingleRearWheelForkliftConfig

class UIBackend:
    """
    Object that will interface between the logic/dynamic simulation part of the 
    extension and the Widget UI
    """
    
    def __init__(self):

        # The window that will be bound to this backend
        self._window = None

        # Get an instance of the Sim Interface
        self._sim_interface: SimInterface = SimInterface()

        # Attribute that holds the currently selected scene from the drowpdown menu
        self._scene_dropdown: ui.AbstractItemModel = None
        self._scene_names = list(SIMULATION_ENVIRONMENTS.keys())

        # Attribute that hold the currently selected vehicle from the dropdown menu
        self._vehicle_dropdown: ui.AbstractItemModel = None
        self._vehicle_names = list(ROBOTS.keys())

        # Get an instance of the vehicle manager
        # self._vehicle_manager = VehicleManager()

        # Selected value for the the id of the vehicle
        self._vehicle_id_field: ui.AbstractValueModel = None
        self._vehicle_id: int = 0

        # Default mode for the extension
        self._mode_field: ui.AbstractItemModel = None
        self._mode: str = "Simulation"

    def set_window_bind(self, window):
        self._window = window

    def set_scene_dropdown(self, scene_dropdown_model: ui.AbstractItemModel):
        self._scene_dropdown = scene_dropdown_model

    def set_vehicle_dropdown(self, vehicle_dropdown_model: ui.AbstractItemModel):
        self._vehicle_dropdown = vehicle_dropdown_model

    def set_vehicle_id_field(self, vehicle_id_field: ui.AbstractValueModel):
        self._vehicle_id_field = vehicle_id_field

    def set_mode_field(self, mode_dropdown_model: ui.AbstractItemModel):
        self._mode_field = mode_dropdown_model

    """
    ---------------------------------------------------------------------
    Callbacks to handle user interaction with the extension widget window
    ---------------------------------------------------------------------
    """

    def on_load_scene(self):
        """
        Method that should be invoked when the button to load the selected world
        is pressed
        """
        # Check if a scene is selected in the drop down menu
        if self._scene_dropdown is not None:

            # Get the ID of the selected environment from the list
            environment_index = self._scene_dropdown.get_item_value_model().as_int

            # Get the name of the selected world
            selected_world = self._scene_names[environment_index]

            # Try to spawn the selected world
            asyncio.ensure_future(self._sim_interface.load_environment_async(SIMULATION_ENVIRONMENTS[selected_world], force_clear=True))

    def on_clear_scene(self):
        """
        Method that should be invoked when the clear world button is pressed
        """
        self._sim_interface.clear_scene()

    def on_load_vehicle(self):
        """
        Method that should be invoked when the button to load the selected vehicle
        is pressed
        """
        async def async_load_vehicle():

            # Check if we already have a physics environment activated. If not, then activate it
            # and only after spawn the vehicle. This is to avoid trying to spawn a vehicle without a physics
            # environment setup. This way we can even spawn a vehicle in an empty world and it won't care
            if hasattr(self._sim_interface.world, '_physics_context') == False:
                await self._sim_interface.world.initialize_simulation_context_async()

            # Check if a vehicle is selected in the drop down
            if self._vehicle_dropdown is not None and self._window is not None:

                # Get the id of the selected vehicle from the list
                vehicle_index = self._vehicle_dropdown.get_item_value_model().as_int

                # Get the name of the selected vehicle
                selected_robot = self._vehicle_names[vehicle_index]

                # Get the id of the selected vehicle
                self._vehicle_id = self._vehicle_id_field.get_value_as_int()

                # Get the desired position and orientation of the vehicle from the UI transform
                pos, euler_angles = self._window.get_selected_vehicle_attitude()

                if selected_robot == "SingleRearWheel":
                    
                    SingleRearWheelForklift(
                        stage_prefix="/World/mono_forklift",
                        usd_path=ROBOTS[selected_robot],
                        vehicle_id=self._vehicle_id,
                        init_pose=pos,
                        init_orientation=Rotation.from_euler("XYZ", euler_angles, degrees=True).as_quat(),
                        # sim_mode=True,
                    )

                #TODO: Launch the selected vehicle

                carb.log_info("Spawned the robot: " + selected_robot + " using the Simulator UI")

            else:
                carb.log_error("Could not spawn the robot using the Simulator UI")

        asyncio.ensure_future(async_load_vehicle())