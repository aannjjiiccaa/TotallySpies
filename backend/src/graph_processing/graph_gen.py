

def generate_graph_json(projectID):
    pass
    # parsed_files = vector_db.fetch_all_metadata(projectID) 
    # """
    # parsed_files: list of dicts, each dict has:
    #   - file_path
    #   - repo
    #   - language
    #   - imports
    #   - symbols_defined
    #   - symbols_used
    # """
    # nodes = []
    # edges = []

    # for file in parsed_files:
    #     file_id = f"{file['repo']}:{file['file_path']}"
    #     nodes.append({
    #         "id": file_id,
    #         "label": file['file_path'].split("/")[-1],
    #         "type": "file",
    #         "repo": file['repo'],
    #         "language": file['language']
    #     })

    #     for sym in file['symbols_defined']:
    #         sym_id = f"{file_id}:{sym}"
    #         nodes.append({
    #             "id": sym_id,
    #             "label": sym,
    #             "type": "class" if sym[0].isupper() else "function",
    #             "parent": file_id
    #         })
    #         edges.append({
    #             "source": file_id,
    #             "target": sym_id,
    #             "type": "contains"
    #         })

    #     for imp in file['imports']:
    #         imp_id = imp  
    #         edges.append({
    #             "source": file_id,
    #             "target": imp_id,
    #             "type": "import"
    #         })

    #     for used in file['symbols_used']:
    #         used_id = f"{file_id}:{used}"  
    #         edges.append({
    #             "source": file_id,
    #             "target": used_id,
    #             "type": "calls"
    #         })

    # return {"nodes": nodes, "edges": edges}
