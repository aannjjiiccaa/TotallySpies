from utils.parsers import *


def get_connections(file):
    lang = detect_language(file)

    if lang == "python":
        return parse_python(file)
    if lang == "c":
        return parse_c(file)
    if lang == "cpp":
        return parse_cpp(file)
    if lang == "java":
        return parse_java(file)

    return {
        "language": "unknown",
        "imports": [],
        "symbols_defined": [],
        "symbols_used": []
    }

def get_embedding(file):
    pass

def get_description(file):
    pass