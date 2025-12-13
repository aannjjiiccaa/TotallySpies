import ast
import os

HTTP_LIBS = {
    "requests",
    "httpx",
    "urllib",
    "aiohttp"
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

    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                module_name = n.name
                abs_path = resolve_import_from_file(file_path, module_name)
                if abs_path:
                    imports.add(abs_path)
                else:
                    packages.add(module_name)

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                module_name = node.module
                abs_path = resolve_import_from_file(file_path, node.module)
                if abs_path:
                    imports.add(abs_path)
                else:
                    packages.add(module_name)

        elif isinstance(node, ast.ClassDef):
            defined.add(node.name)

        elif isinstance(node, ast.FunctionDef):
            defined.add(node.name)

        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                base = node.func.value
                func_name = node.func.attr

                if isinstance(base, ast.Name) and base.id in HTTP_LIBS:
                    url = extract_url(node)
                    http_calls.append({
                        "library": base.id,
                        "method": func_name,
                        "url": url,
                        "file": file_path,
                        "lineno": node.lineno
                    })

    return {
        "language": "python",
        "imports": list(imports),
        "packages": list(packages),
        "symbols_defined": list(defined),
        "symbols_used": list(used),
        "http_calls": http_calls
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

def extract_url(call_node):
    if not call_node.args:
        return None

    arg = call_node.args[0]

    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
        return arg.value

    if isinstance(arg, ast.Call):
        if isinstance(arg.func, ast.Attribute):
            if arg.func.attr == "getenv":
                if arg.args and isinstance(arg.args[0], ast.Constant):
                    return f"ENV:{arg.args[0].value}"

    return "dynamic"
