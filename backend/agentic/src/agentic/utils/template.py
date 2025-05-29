import inspect
import os
import sys
from typing import Optional

def find_template_path() -> Optional[str]:
    """Find the template path based on the caller's file location."""
    try:
        # Look for frames outside this file
        frame = inspect.currentframe()
        while frame:
            # Skip frames from this file
            if frame.f_code.co_filename == __file__:
                frame = frame.f_back
                continue
            
            # Found a frame from another file
            caller_file = frame.f_code.co_filename
            
            # Check if there's a matching template file
            directory = os.path.dirname(caller_file)
            base = os.path.splitext(os.path.basename(caller_file))[0]
            template_path = os.path.join(directory, f"{base}.prompts.yaml")
            
            if os.path.exists(template_path):
                return template_path
                
            # If not found, check the module
            try:
                module_name = frame.f_globals.get('__name__')
                if module_name and '.' not in module_name:
                    module = sys.modules.get(module_name)
                    if module and hasattr(module, '__file__'):
                        module_file = module.__file__
                        module_dir = os.path.dirname(module_file)
                        module_base = os.path.splitext(os.path.basename(module_file))[0]
                        module_template = os.path.join(module_dir, f"{module_base}.prompts.yaml")
                        
                        if os.path.exists(module_template):
                            return module_template
            except Exception as e:
                print(f"Warning: Error checking module template: {e}")
            
            frame = frame.f_back
            
        # Last resort: try to find a template based on class name
        caller_frame = inspect.currentframe().f_back
        if caller_frame and 'self' in caller_frame.f_locals:
            self_obj = caller_frame.f_locals['self']
            if self_obj.__class__.__name__ not in ("BaseAgentProxy", "AgentProxyClass"):
                class_base = self_obj.__class__.__name__.lower()
                if class_base.endswith('agent'):
                    class_base = class_base[:-5]  # Strip 'agent' suffix
                
                # Look in current dir and parents
                cwd = os.getcwd()
                for _ in range(3):  # Current + 2 parent dirs
                    for filename in (f"{class_base}.prompts.yaml", f"{class_base}_agent.prompts.yaml"):
                        template_path = os.path.join(cwd, filename)
                        if os.path.exists(template_path):
                            return template_path
                    
                    # Go up one level
                    parent = os.path.dirname(cwd)
                    if parent == cwd:  # Hit root
                        break
                    cwd = parent
        
    except Exception as e:
        print(f"Warning: Error finding template path: {e}")
    
    return None