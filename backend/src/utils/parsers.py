import ast
import re

def detect_language(file_path):
    if file_path.endswith(".py"):
        return "python"
    if file_path.endswith((".c", ".h")):
        return "c"
    if file_path.endswith((".cpp", ".hpp", ".cc")):
        return "cpp"
    if file_path.endswith(".java"):
        return "java"
    return "unknown"


def parse_python(file_path):
    imports = set()
    defined = set()
    used = set()

    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imports.add(n.name)

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module)

        elif isinstance(node, ast.ClassDef):
            defined.add(node.name)

        elif isinstance(node, ast.FunctionDef):
            defined.add(node.name)

        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                used.add(node.func.id)

    return {
        "language": "python",
        "imports": list(imports),
        "symbols_defined": list(defined),
        "symbols_used": list(used)
    }


def parse_c(file_path):
    imports = set()
    defined = set()
    used = set()

    with open(file_path) as f:
        code = f.read()

    includes = re.findall(r'#include\s+[<"](.+?)[">]', code)
    imports.update(includes)

    funcs = re.findall(r'\b([a-zA-Z_]\w*)\s*\([^;]*\)\s*\{', code)
    defined.update(funcs)

    calls = re.findall(r'\b([a-zA-Z_]\w*)\s*\(', code)
    used.update(calls)

    return {
        "language": "c",
        "imports": list(imports),
        "symbols_defined": list(defined),
        "symbols_used": list(used)
    }

def parse_cpp(file_path):
    imports = set()
    defined = set()
    used = set()

    with open(file_path) as f:
        code = f.read()

    imports.update(re.findall(r'#include\s+[<"](.+?)[">]', code))

    classes = re.findall(r'class\s+(\w+)', code)
    defined.update(classes)

    funcs = re.findall(r'\b([a-zA-Z_]\w*)\s*\([^;]*\)\s*\{', code)
    defined.update(funcs)

    calls = re.findall(r'\b([a-zA-Z_]\w*)\s*\(', code)
    used.update(calls)

    return {
        "language": "cpp",
        "imports": list(imports),
        "symbols_defined": list(defined),
        "symbols_used": list(used)
    }

def parse_java(file_path):
    imports = set()
    defined = set()
    used = set()

    with open(file_path) as f:
        code = f.read()

    imports.update(re.findall(r'import\s+([\w\.]+);', code))
    classes = re.findall(r'class\s+(\w+)', code)
    defined.update(classes)

    methods = re.findall(r'\b(\w+)\s*\([^)]*\)\s*\{', code)
    defined.update(methods)

    calls = re.findall(r'\b(\w+)\s*\(', code)
    used.update(calls)

    return {
        "language": "java",
        "imports": list(imports),
        "symbols_defined": list(defined),
        "symbols_used": list(used)
    }