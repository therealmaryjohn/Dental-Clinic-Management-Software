# utils/refresh_utils.py

def refresh_module(module_instance):
    """
    Calls standard refresh methods on a module instance if they exist.
    """
    if hasattr(module_instance, "load_patients"):
        module_instance.load_patients()
    if hasattr(module_instance, "load_appointments"):
        module_instance.load_appointments()
    if hasattr(module_instance, "load_data"):
        module_instance.load_data()
    if hasattr(module_instance, "refresh"):
        module_instance.refresh()
