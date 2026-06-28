import os
import logging
from typing import Dict, Any
from azure.identity import AzureCliCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.core.exceptions import AzureError

logger = logging.getLogger(__name__)


class AzureVMManager:
    """Service layer class to manage the lifecycle of a single configured Azure VM."""

    def __init__(self):
        """Initializes the Azure VM Manager by loading configurations and establishing client connection."""
        self.subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID")
        self.resource_group = os.environ.get("AZURE_RESOURCE_GROUP")
        self.vm_name = os.environ.get("AZURE_VM_NAME")

        # Validate that all required configuration parameters are available
        if not self.subscription_id or not self.resource_group or not self.vm_name:
            raise ValueError(
                "Missing required Azure VM configurations. Ensure AZURE_SUBSCRIPTION_ID, "
                "AZURE_RESOURCE_GROUP, and AZURE_VM_NAME are set in your .env file."
            )

        try:
            # Authenticate using Azure CLI credentials
            self.credential = AzureCliCredential()
            # Initialize ComputeManagementClient
            self.client = ComputeManagementClient(self.credential, self.subscription_id)
        except Exception as e:
            logger.error(f"Failed to initialize Azure clients: {e}")
            raise RuntimeError(f"Azure authentication or client initialization failed: {e}")

    def start_vm(self) -> Dict[str, Any]:
        """Starts the configured Azure VM.

        Triggers the start operation asynchronously and returns immediately.
        """
        try:
            logger.info(f"Initiating start for VM '{self.vm_name}' in resource group '{self.resource_group}'")
            self.client.virtual_machines.begin_start(self.resource_group, self.vm_name)
            return {"success": True, "message": f"VM '{self.vm_name}' start initiated."}
        except AzureError as e:
            logger.error(f"Azure SDK error starting VM '{self.vm_name}': {e}")
            return {"success": False, "error": f"Azure operation failed: {e.message if hasattr(e, 'message') else str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error starting VM '{self.vm_name}': {e}")
            return {"success": False, "error": f"Failed to start VM: {str(e)}"}

    def stop_vm(self) -> Dict[str, Any]:
        """Stops the configured Azure VM (PowerOff - resources are still allocated/billed).

        Triggers the stop operation asynchronously and returns immediately.
        """
        try:
            logger.info(f"Initiating power-off/stop for VM '{self.vm_name}' in resource group '{self.resource_group}'")
            self.client.virtual_machines.begin_power_off(self.resource_group, self.vm_name)
            return {"success": True, "message": f"VM '{self.vm_name}' stop initiated."}
        except AzureError as e:
            logger.error(f"Azure SDK error stopping VM '{self.vm_name}': {e}")
            return {"success": False, "error": f"Azure operation failed: {e.message if hasattr(e, 'message') else str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error stopping VM '{self.vm_name}': {e}")
            return {"success": False, "error": f"Failed to stop VM: {str(e)}"}

    def restart_vm(self) -> Dict[str, Any]:
        """Restarts the configured Azure VM.

        Triggers the restart operation asynchronously and returns immediately.
        """
        try:
            logger.info(f"Initiating restart for VM '{self.vm_name}' in resource group '{self.resource_group}'")
            self.client.virtual_machines.begin_restart(self.resource_group, self.vm_name)
            return {"success": True, "message": f"VM '{self.vm_name}' restart initiated."}
        except AzureError as e:
            logger.error(f"Azure SDK error restarting VM '{self.vm_name}': {e}")
            return {"success": False, "error": f"Azure operation failed: {e.message if hasattr(e, 'message') else str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error restarting VM '{self.vm_name}': {e}")
            return {"success": False, "error": f"Failed to restart VM: {str(e)}"}

    def deallocate_vm(self) -> Dict[str, Any]:
        """Deallocates the configured Azure VM (stops billing for VM compute).

        Triggers the deallocation operation asynchronously and returns immediately.
        """
        try:
            logger.info(f"Initiating deallocation for VM '{self.vm_name}' in resource group '{self.resource_group}'")
            self.client.virtual_machines.begin_deallocate(self.resource_group, self.vm_name)
            return {"success": True, "message": f"VM '{self.vm_name}' deallocation initiated."}
        except AzureError as e:
            logger.error(f"Azure SDK error deallocating VM '{self.vm_name}': {e}")
            return {"success": False, "error": f"Azure operation failed: {e.message if hasattr(e, 'message') else str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error deallocating VM '{self.vm_name}': {e}")
            return {"success": False, "error": f"Failed to deallocate VM: {str(e)}"}

    def get_vm_status(self) -> Dict[str, Any]:
        """Retrieves the current power state/status of the configured Azure VM."""
        try:
            logger.info(f"Fetching status for VM '{self.vm_name}' in resource group '{self.resource_group}'")
            # Retrieve the instance view which contains the power state
            vm_details = self.client.virtual_machines.get(
                self.resource_group, self.vm_name, expand="instanceView"
            )

            power_state = "Unknown"
            if vm_details.instance_view and vm_details.instance_view.statuses:
                for status in vm_details.instance_view.statuses:
                    if status.code and status.code.startswith("PowerState/"):
                        # Extract state name (e.g. 'PowerState/running' -> 'running')
                        raw_state = status.code.split("/")[-1].lower()
                        # Map raw state to a consistent status string expected by the frontend
                        state_mapping = {
                            "running": "Running",
                            "starting": "Starting",
                            "stopping": "Stopping",
                            "stopped": "Stopped",
                            "deallocating": "Stopping",
                            "deallocated": "Deallocated",
                        }
                        power_state = state_mapping.get(raw_state, raw_state.capitalize())
                        break

            return {
                "success": True,
                "status": power_state,
                "vm_name": self.vm_name,
                "resource_group": self.resource_group
            }
        except AzureError as e:
            logger.error(f"Azure SDK error retrieving status for VM '{self.vm_name}': {e}")
            return {"success": False, "error": f"Azure status retrieval failed: {e.message if hasattr(e, 'message') else str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error retrieving status for VM '{self.vm_name}': {e}")
            return {"success": False, "error": f"Failed to get VM status: {str(e)}"}
