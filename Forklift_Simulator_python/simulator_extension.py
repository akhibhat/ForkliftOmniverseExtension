"""
| File: simulator_extension.py
| Author: Akhilesh Bhat
| Description: Implements the Pegasus_SimulatorExtension which omni.ext.IExt that is created when this class is enabled. In turn, this class initializes the extension widget.
"""

__all__ = ["SimulatorExtension"]

import gc
import asyncio
from functools import partial
from threading import Timer 

# Omniverse general API
import pxr 
import carb 
import omni.ext
import omni.usd
import omni.kit.ui
import omni.kit.app
import omni.ui as ui

from omni.kit.viewport.utility import get_active_viewport

# Extension files and API
from .global_variables import WINDOW_TITLE, MENU_PATH
from .logic.interface.simulation_interface import SimInterface 

# Setting up the UI for the extension's widget
from .ui.sim_ui_window import WidgetWindow
from .ui.ui_backend import UIBackend 

class SimulatorExtension(omni.ext.IExt):
    # ext_id is current extension id. It can be used with the extension manager to query
    # additional information
    def on_startup(self, ext_id):

        carb.log_info("Simulator is starting")

        # Save the extension id
        self._ext_id = ext_id

        # Create the UI of the app and its manager
        self.ui_backend = None
        self.ui_window = None

        self._sim_interface = SimInterface()

        # Check if we have a stage loaded (when using autoload feature, it might not be ready yet)
        # This is a limitation of the simulator, and we are doing this to ensure that the extension
        # does not crash when using the GUI with autoload feature.
        # If autoload was not enabled, and we are enabling the extension from the Extension widget,
        # then we will always have a state open, and the auxiliary timer will never run.
        if omni.usd.get_context().get_stage_state() != omni.usd.StageState.CLOSED:
            self._sim_interface.initialize_world()
        else:
            self.autoload_helper()

        ui.Workspace.set_show_window_fn(WINDOW_TITLE, partial(self.show_window, None))

        # Add the extension to the editor menu inside Isaac Sim
        editor_menu = omni.kit.ui.get_editor_menu()
        if editor_menu:
            self._menu = editor_menu.add_item(MENU_PATH, self.show_window, toggle=True, value=True)

        # Show the window
        ui.Workspace.show_window(WINDOW_TITLE, show=True)
        
    def autoload_helper(self):

        # Check if we already have a viewport and a camera of interest
        if get_active_viewport() != None and type(get_active_viewport().stage) == pxr.Usd.Stage and str(get_active_viewport().stage.GetPrimAtPath("/OmniverseKit_Persp")) != "invalid null prim":
            self._sim_interface.initialize_world()
        else:
            Timer(0.1, self.autoload_helper).start()

    def show_window(self, menu, show):
        """
        Method that controls whether a widget window is created or not
        """
        if show == True:
            # Create a window and its backend
            self.ui_backend = UIBackend()
            self.ui_window = WidgetWindow(self.ui_backend)
            self.ui_window.set_visibility_changed_fn(self._visibility_changed_fn)

        # If we have a window and we are not supposed to show it, change its visibility
        elif self.ui_window:
            self.ui_window.visible = False

    def _visibility_changed_fn(self, visible):
        """
        This method is invoked when the used pressed the "X" to close the extension window
        """

        # Update the Isaac sim menu visibility
        

        if not visible:
            # Destroy the window, because we create a new one in the show window method
            asyncio.ensure_future(self._destroy_window_async())

    async def _destroy_window_async(self):

        # Wait one frame before it gets destructed
        await omni.kit.app.get_app().next_update_async()

        # Destroy the window UI if it exists
        if self.ui_window:
            self.ui_window.destroy()
            self.ui_window = None

    def on_shutdown(self):
        """
        Callback when the extension is shutdown
        """
        carb.log_info("Simulator Extension shutdown")

        # Destroy the isaac sim menu object


        # Destroy the window
        if self.ui_window:
            self.ui_window.destroy()
            self.ui_window = None

        # Destroy the backend
        if self.ui_backend:
            self.ui_backend = None

        # De-register the function that shows the window from the isaac sim ui
        ui.Workspace.set_show_window_fn(WINDOW_TITLE, None)

        gc.collect()