import ast
import os
from pathlib import Path
from typing import Any, Optional, Dict, List

from .url_extractor import URLExtractor

HTTP_LIBS = {
    "requests",
    "httpx",
    "urllib",
    "aiohttp"
}

ROUTE_DECORATORS = {
    "route",
    "get", "post", "put", "delete", "patch",
    "head", "options", "trace",
}

def detect_language(file_path):
    file_path = str(file_path)
    if file_path.endswith(".py"):
        return "python"
    elif file_path.endswith(".c"):
        return "c"
    elif file_path.endswith(".cpp"):
        return "cpp"
    elif file_path.endswith(".java"):
        return "java"
    else:
        return "unknown"


def parse_python(file_path):
    imports = set()
    defined = set()
    packages = set()
    used = set()
    http_calls = []
    routes = []

    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())
    extractor = URLExtractor()
    extractor.visit(tree)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                module_name = n.name
                abs_path = resolve_import_from_file(file_path, module_name)
                if abs_path:
                    imports.add(str(abs_path))
                else:
                    packages.add(module_name)

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                module_name = node.module
                abs_path = resolve_import_from_file(file_path, node.module)
                if abs_path:
                    imports.add(str(abs_path))
                else:
                    packages.add(module_name)

        elif isinstance(node, ast.ClassDef):
            defined.add(node.name)
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    defined.add(item.name)
                    method_routes = extract_routes_from_function(item, file_path, node.name)
                    routes.extend(method_routes)
            defined.add(node.name)

        elif isinstance(node, ast.FunctionDef):
            defined.add(node.name)
            function_routes = extract_routes_from_function(node, file_path)
            routes.extend(function_routes)

        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                base = node.func.value
                func_name = node.func.attr

                if isinstance(base, ast.Name) and base.id in HTTP_LIBS:
                    url = extractor.extract_url(node)
                    http_calls.append({
                        "library": base.id,
                        "method": func_name,
                        "url": url,
                        "file": str(file_path),
                        "lineno": node.lineno
                    })

    return {
        "language": "python",
        "imports": list(imports),
        "packages": list(packages),
        "symbols_defined": list(defined),
        "symbols_used": list(used),
        "http_calls": http_calls,
        "routes": routes
    }

def resolve_import_from_file(current_file_path, module_name):
    base_dir = os.path.dirname(os.path.abspath(current_file_path))
    parts = module_name.split(".") 
    search_dir = base_dir
    while True:
        candidate = os.path.join(search_dir, *parts) 
        py_file = candidate + ".py"                 
        
        if os.path.isfile(py_file):
            return os.path.abspath(py_file)
        elif os.path.isfile(os.path.join(candidate, "__init__.py")):
            return os.path.abspath(os.path.join(candidate, "__init__.py"))
        
        parent = os.path.dirname(search_dir)
        if parent == search_dir:
            break
        search_dir = parent
    
    return None

def extract_route_from_decorator(decorator_node: ast.Call) -> Optional[Dict[str, Any]]:
    try:
        if isinstance(decorator_node.func, ast.Attribute):
            if decorator_node.func.attr in ROUTE_DECORATORS:
                method = decorator_node.func.attr.upper() if decorator_node.func.attr != "route" else None
                
                if decorator_node.args:
                    first_arg = decorator_node.args[0]
                    if isinstance(first_arg, ast.Constant) and isinstance(first_arg.value, str):
                        path = first_arg.value
                        
                        if decorator_node.func.attr == "route" and len(decorator_node.args) > 1:
                            methods = ["GET"] 
                            for kw in decorator_node.keywords:
                                if kw.arg == "methods" and isinstance(kw.value, ast.List):
                                    methods = [elt.value.upper() if isinstance(elt, ast.Constant) else None 
                                              for elt in kw.value.elts]
                                    methods = [m for m in methods if m]  
                            
                            return {
                                "path": path,
                                "methods": methods,
                                "decorator": "route"
                            }
                        else:
                            method = decorator_node.func.attr.upper()
                            return {
                                "path": path,
                                "methods": [method],
                                "decorator": decorator_node.func.attr
                            }
        
        elif isinstance(decorator_node.func, ast.Attribute):
            if decorator_node.func.attr in ["api_route", "add_api_route"]:
                if decorator_node.args and isinstance(decorator_node.args[0], ast.Constant):
                    path = decorator_node.args[0].value
                    methods = ["GET"]
                    for kw in decorator_node.keywords:
                        if kw.arg == "methods" and isinstance(kw.value, ast.List):
                            methods = [elt.value.upper() if isinstance(elt, ast.Constant) else None 
                                      for elt in kw.value.elts]
                            methods = [m for m in methods if m]
                    
                    return {
                        "path": path,
                        "methods": methods,
                        "decorator": decorator_node.func.attr
                    }
    
    except (AttributeError, TypeError):
        pass
    
    return None

def extract_routes_from_function(func_node: ast.FunctionDef, file_path: str, class_name: str = None) -> List[Dict[str, Any]]:
    routes = []
    
    for decorator in func_node.decorator_list:
        if isinstance(decorator, ast.Call):
            route_info = extract_route_from_decorator(decorator)
            if route_info:
                route_info.update({
                    "function_name": func_node.name,
                    "class_name": class_name,
                    "file": str(file_path),
                    "lineno": func_node.lineno,
                    "full_path": f"{class_name}.{func_node.name}" if class_name else func_node.name
                })
                routes.append(route_info)
        
        elif isinstance(decorator, ast.Attribute):
            pass
        
        elif isinstance(decorator, ast.Name):
            pass
    
    return routes