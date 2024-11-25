"""
| File: simulation_interface.py
| Author: Akhilesh Bhat
| Description: Definition of the PegasusInterface class (a singleton) that is used to manage the Pegasus framework.
"""

__all__ = ["SimInterface"]

import gc
import yaml
import os
import asyncio
from threading import Lock

# NVidia API imports
import carb
from omni.isaac.core.world import World
from omni.isaac.core.utils.stage import clear_stage
import omni.isaac.core.utils.nucleus as nucleus

# from scripts.logic.vehicle_manager import VehicleManager
from Forklift_Simulator_python.global_variables import DEFAULT_WORLD_SETTINGS, SIMULATION_ENVIRONMENTS

class SimInterface:
    """
    SimInterface is a singleton class (there is only one object instance at any given time)
    that will be used 
    """

    # The object instance of the Vehicle Manager
    _instance = None
    _is_initialized = False

    # Lock for safe multi-threading
    _lock: Lock = Lock()

    def __init__(self):
        """
        Initialize the SimInterface singleton object (only runs once at a time)
        """

        # If we already have an instance of the SimInterface, do not overwrite it
        if SimInterface._is_initialized:
            return
        
        carb.log_info("Initializing the Simulation Interface Extension")
        SimInterface._is_initialized = True

        # Get a handle to the vehicle manager instance which will manage which vehicles
        # are spawned in the world to be controlled and simulated
        # self._vehicle_manager = VehicleManager()

        # Initialize the world with the default simulation settings
        self._world_settings = DEFAULT_WORLD_SETTINGS
        self._world = None

    @property
    def world(self):
        """ The current omni.isaac.core.world World instance

        Returns:
            omni.isaac.core.world: The world instance
        """
        return self._world
    
    # @property
    # def vehicle_manager(self):
    #     """ The instance of the VehicleManager

    #     Returns:
    #         VehicleManager: The current instance of the VehicleManager
    #     """
    #     return self._vehicle_manager
    
    def initialize_world(self):
        """ Method that initializes the world object
        """

        self._world = World(**self._world_settings)

    # def get_vehicle(self, stage_prefix: str):
    #     """ Method that returns the vehicle object given its stage_prefix

    #     Args:
    #         stage_prefix (str): The name the vehicle will present in the simulator when spawned

    #     Returns:
    #         Vehicle: Returns a vehicle object that was spawned with the given stage_prefix
    #     """
    #     return self._vehicle_manager.vehicles[stage_prefix]
    
    # def get_all_vehicles(self):
    #     """ Method that returns a list of all vehicles that are considered active in the simulator
        
    #     Returns:
    #         list: A list of all vehicles that are currently instantiated
    #     """
    #     return self._vehicle_manager.vehicles
    
    def get_default_environments(self):
        """
        Method that returns a dictionary containing all the default simulation environments and their path
        """
        return SIMULATION_ENVIRONMENTS
    
    def clear_scene(self):
        """
        Method that when invoked will clear all vehicles and the simulation environment,
        leaving only an empty world with a physics environment
        """

        # If the physics simulation was running, stop it first
        if self.world is not None:
            self.world.stop()

        # Clear the world
        if self.world is not None:
            self.world.clear_all_callbacks()
            self.world.clear()

        # Clear the stage
        clear_stage()

        # Remove all the robots that were spawned
        # self._vehicle_manager.remove_all_vehicles()

        # Call python's garbage collection
        gc.collect()

        # Re-initialize the physics context
        asyncio.ensure_future(self._world.initialize_simulation_context_async())
        carb.log_info("Current scene and its vehicles has been deleted")

    async def load_environment_async(self, usd_path: str, force_clear: bool=False):
        """ Method that loads a given world (specified in the usd_path) into the simulator asynchronously.

        Args:
            usd_path (str): The path where the USD file describing the world is located.
            force_clear (bool): Whether to perform a clear before loading the asset. Defaults to False.
        """

        # Reset and pause the world simulation (only if force_clear is true)
        # This is done to maximize the support between running in GUI as extension vs app
        if force_clear == True:
            await self.world.reset_async()
            await self.world.stop_async()

        # Load the USD asset that will be used for the environment
        try:
            self.load_asset(usd_path, "/World/layout")
        except Exception as e:
            carb.log_warn("Could not load the desired environment: " + str(e))

        carb.log_info("A new environment has been loaded successfully")

    def load_environment(self, usd_path: str, force_clear: bool=False):
        """Method that loads a given world (specified in the usd_path) into the simulator. If invoked from a python app,
        this method should have force_clear=False, as the world reset and stop are performed asynchronously by this method, 
        and when we are operating in App mode, we want everything to run in sync.

        Args:
            usd_path (str): The path where the USD file describing the world is located.
            force_clear (bool): Whether to perform a clear before loading the asset. Defaults to False.
        """
        asyncio.ensure_future(self.load_environment_async(usd_path, force_clear))

    def load_nvidia_environment(self, environment_asset: str = "Hospital/hospital.usd"):
        """
        Method that is used to load NVidia internally provided USD stages into the simulaton World

        Args:
            environment_asset (str): The name of the nvidia asset inside the /Isaac/Environments folder. Default to Hospital/hospital.usd.
        """

        # Get the nvidia assets root path
        nvidia_assets_path = nucleus.get_assets_root_path()

        # Define the environments path inside the NVidia assets
        environments_path = "/Isaac/Environments"

        # Get the complete usd path
        usd_path = nvidia_assets_path + environments_path + "/" + environment_asset

        # Try to load the asset into the world
        self.load_asset(usd_path, "/World/layout")

    def load_asset(self, usd_asset: str, stage_prefix: str):
        """
        Method that will attempt to load an asset into the current simulation world, given the USD asset path.

        Args:
            usd_asset (str): The path where the USD file describing the world is located.
            stage_prefix (str): The name the vehicle will present in the simulator when spawned. 
        """

        # Try to check if there is already a prim with the same stage prefix in the stage
        if self._world.stage.GetPrimAtPath(stage_prefix):
            raise Exception("A primitive already exists at the specified path")

        # Create the stage primitive and load the usd into it
        prim = self._world.stage.DefinePrim(stage_prefix)
        success = prim.GetReferences().AddReference(usd_asset)

        if not success:
            raise Exception("The usd asset" + usd_asset + "is not loaded at stage path " + stage_prefix)
        
    def set_world_settings(self, physics_dt=None, stage_units_in_meters=None, rendering_dt=None):
        """
        Set the current world settings to the pre-defined settings. TODO - finish the implementation of this method.
        For now these new setting will never override the default ones.
        """

        # Set the physics engine update rate
        if physics_dt is not None:
            self._world_settings["physics_dt"] = physics_dt

        # Set the units of the simulator to meters
        if stage_units_in_meters is not None:
            self._world_settings["stage_units_in_meters"] = stage_units_in_meters

        # Set the render engine update rate (might not be the same as the physics engine)
        if rendering_dt is not None:
            self._world_settings["rendering_dt"] = rendering_dt

    def __new__(cls):
        """Allocates the memory and creates the actual PegasusInterface object is not instance exists yet. Otherwise,
        returns the existing instance of the PegasusInterface class.

        Returns:
            SimInterface: the single instance of the SimInterface class
        """

        # Use a lock in here to make sure we do not have a race condition
        # when using multi-threading and creating the first instance of the Pegasus extension manager
        with cls._lock:
            if cls._instance is None:
                cls._instance = object.__new__(cls)

        return SimInterface._instance

    def __del__(self):
        """Destructor for the object. Destroys the only existing instance of this class."""
        SimInterface._instance = None
        SimInterface._is_initialized = False