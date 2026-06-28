from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from .services.azure_manager import AzureVMManager


def _get_manager_or_error():
    """Helper method to instantiate the Azure VM Manager or catch configuration/auth errors."""
    try:
        return AzureVMManager(), None
    except Exception as e:
        return None, str(e)


@require_POST
def start_vm(request):
    """API endpoint to start the Azure VM."""
    manager, error = _get_manager_or_error()
    if error:
        return JsonResponse({"success": False, "error": error}, status=500)

    response_data = manager.start_vm()
    status_code = 200 if response_data.get("success") else 500
    return JsonResponse(response_data, status=status_code)


@require_POST
def stop_vm(request):
    """API endpoint to stop/power off the Azure VM."""
    manager, error = _get_manager_or_error()
    if error:
        return JsonResponse({"success": False, "error": error}, status=500)

    response_data = manager.stop_vm()
    status_code = 200 if response_data.get("success") else 500
    return JsonResponse(response_data, status=status_code)


@require_POST
def restart_vm(request):
    """API endpoint to restart the Azure VM."""
    manager, error = _get_manager_or_error()
    if error:
        return JsonResponse({"success": False, "error": error}, status=500)

    response_data = manager.restart_vm()
    status_code = 200 if response_data.get("success") else 500
    return JsonResponse(response_data, status=status_code)


@require_POST
def deallocate_vm(request):
    """API endpoint to deallocate the Azure VM."""
    manager, error = _get_manager_or_error()
    if error:
        return JsonResponse({"success": False, "error": error}, status=500)

    response_data = manager.deallocate_vm()
    status_code = 200 if response_data.get("success") else 500
    return JsonResponse(response_data, status=status_code)


@require_GET
def get_status(request):
    """API endpoint to retrieve the current VM status."""
    manager, error = _get_manager_or_error()
    if error:
        return JsonResponse({"success": False, "error": error}, status=500)

    response_data = manager.get_vm_status()
    status_code = 200 if response_data.get("success") else 500
    return JsonResponse(response_data, status=status_code)
