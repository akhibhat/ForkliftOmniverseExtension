# Copyright (c) 2022-2023, NVIDIA CORPORATION. All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto. Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import os 
from pathlib import Path 

import omni.isaac.core.utils.nucleus as nucleus

EXTENSION_TITLE = "Forklift Simulator"
WINDOW_TITLE = "Forklift Simulator"
MENU_PATH = "Window/" + WINDOW_TITLE

EXTENSION_DESCRIPTION = "Warehouse Simulator for forklifts"

DEFAULT_WORLD_SETTINGS = {"physics_dt": 1.0 / 250.0, "stage_units_in_meters": 1.0, "rendering_dt": 1.0 / 60.0}

# Get the current directory of where this extension is located
EXTENSION_FOLDER_PATH = Path(os.path.dirname(os.path.realpath(__file__)))
ROOT = str(EXTENSION_FOLDER_PATH.parent.resolve())

# Define the Extension Assets Path
ASSET_PATH = ROOT + "/assets"
ROBOT_ASSETS = ASSET_PATH + "/Robots"

SIMULATION_ENVIRONMENTS = {}

# Setup the default simulation environments path
NVIDIA_ASSETS_PATH = str(nucleus.get_assets_root_path())
ISAAC_SIM_ENVIRONMENTS = "/Isaac/Environments"
NVIDIA_SIMULATION_ENVIRONMENTS = {
    "Default Environment": "Grid/default_environment.usd",
    "Black Gridroom": "Grid/gridroom_black.usd",
    "Curved Gridroom": "Grid/gridroom_curved.usd",
    "Hospital": "Hospital/hospital.usd",
    "Office": "Office/office.usd",
    "Simple Room": "Simple_Room/simple_room.usd",
    "Warehouse": "Simple_Warehouse/warehouse.usd",
    "Warehouse with Forklifts": "Simple_Warehouse/warehouse_with_forklifts.usd",
    "Warehouse with Shelves": "Simple_Warehouse/warehouse_multiple_shelves.usd",
    "Full Warehouse": "Simple_Warehouse/full_warehouse.usd",
    "Flat Plane": "Terrains/flat_plane.usd",
    "Rough Plane": "Terrains/rough_plane.usd",
    "Slope Plane": "Terrains/slope.usd",
    "Stairs Plane": "Terrains/stairs.usd",
}
NVIDIA_ROBOTS = "/Isaac/Robots"
#TODO: Fix paths
ROBOTS = {
    "Rack": ROBOT_ASSETS + "/RackForklift/forklift.usd",
    "Reach": ROBOT_ASSETS + "/ReachForklift/forklift.usd",
    "SingleRearWheel": NVIDIA_ASSETS_PATH + NVIDIA_ROBOTS + "/Forklift/forklift_b.usd",
}

# Add the Isaac Sim assets to the list
for asset in NVIDIA_SIMULATION_ENVIRONMENTS:
    SIMULATION_ENVIRONMENTS[asset] = (
        NVIDIA_ASSETS_PATH + ISAAC_SIM_ENVIRONMENTS + "/" + NVIDIA_SIMULATION_ENVIRONMENTS[asset]
    )