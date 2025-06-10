# Created by Gemini
import os
import shutil

DIR = "25-adt-chc-comp"

def process_smt2_files(source_sub_dirs, destination_dir, base_directory):
    """
    Recursively searches specified directories, copies and renames .smt2 files,
    and returns a list of copied file names.
    """
    full_source_dirs = [os.path.join(base_directory, d) for d in source_sub_dirs]

    os.makedirs(destination_dir, exist_ok=True)

    copied_files_list = []
    file_counter = 1

    for source_dir in full_source_dirs:
        if not os.path.isdir(source_dir):
            print(f"Warning: Source directory '{source_dir}' not found. Skipping.")
            continue

        for root, _, files in os.walk(source_dir):
            for file in files:
                if file.endswith(".smt2"):
                    source_file_path = os.path.join(root, file)

                    relative_path_from_base = os.path.relpath(source_file_path, start=base_directory)
                    unique_name_suffix_no_ext = os.path.splitext(relative_path_from_base.replace(os.sep, '-'))[0]

                    new_file_name = f"{file_counter:03d}-{unique_name_suffix_no_ext}.smt2"
                    destination_file_path = os.path.join(destination_dir, new_file_name)

                    try:
                        shutil.copy2(source_file_path, destination_file_path)
                        copied_files_list.append(os.path.join(destination_dir, new_file_name))
                        print(f"Copied: {source_file_path} -> {destination_file_path}")
                        file_counter += 1
                    except Exception as e:
                        print(f"Error copying file: {source_file_path} -> {destination_file_path}: {e}")

    return copied_files_list

def write_lists_file(file_list, output_file):
    """
    Writes a list of copied file names (basenames) to a file, one per line.
    """
    try:
        with open(output_file, 'w') as f:
            for file_path in file_list:
                f.write(f"{DIR}/{os.path.basename(file_path)}\n")
        print(f"File list written to '{output_file}'.")
    except Exception as e:
        print(f"Error writing file list: {e}")

if __name__ == "__main__":
    # Base directory where the source sub-directories are located
    BASE_DIRECTORY = "/home/katsura/github.com/chc-comp/chc-comp25-benchmarks"

    # Sub-directories to search within the BASE_DIRECTORY
    source_sub_directories = [
        "adt-purified-benchmarks",
        "tip-adt-lia",
        "rust-horn",
        "ringen-adt-benchmarks",
        "ADTRem"
    ]
    
    # Destination directory for the copied files
    destination_directory = f"inputs/{DIR}"
    
    # Output file for the list of copied file names
    output_list_file = "lists/25-adt-chccomp"

    copied_files = process_smt2_files(source_sub_directories, destination_directory, BASE_DIRECTORY)
    write_lists_file(copied_files, output_list_file)
