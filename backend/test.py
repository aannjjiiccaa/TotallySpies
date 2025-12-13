
import os
from src.utils.iterate_cloning_dir import iter_files
from src.utils.process_file import get_connections
CLONING_DIR = r"C:\Users\mestr\OneDrive\Desktop\TotallySpies\TotallySpies\backend\src\cloning_dir"

os.makedirs(CLONING_DIR, exist_ok=True)

def main():
    for file in iter_files(CLONING_DIR):
        connections = get_connections(file)
        print(connections['imports'])

if __name__ == '__main__':
    main()