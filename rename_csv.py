import os
import re
import shutil

original_root = "data"  # 原始目录
new_root = "data_new"  # 新目录

categories = ["curved", "straight", "tilted", "rotate"]
normal_dirs = ["up","down","left","right"]

rotate_map = {
    "ccw": ["ccw", "counter_clockwise"],
    "cw": ["cw", "clockwise"]
    
}

categories_set = set(categories)
normal_dirs_set = set(normal_dirs)

def unify_rotate_direction(name_part):
    lower_name = name_part.lower()
    for std_dir, variants in rotate_map.items():
        for v in variants:
            if v in lower_name:
                return std_dir
    return None

def find_category_in_path(path_parts):
    for p in path_parts:
        if p.lower() in categories_set:
            return p.lower()
    return None

def find_direction(category, path_parts, filename):
    lower_parts = [p.lower() for p in path_parts]
    lower_filename = filename.lower()
    
    if category == "rotate":
        for part in lower_parts:
            d = unify_rotate_direction(part)
            if d is not None:
                return d
        d = unify_rotate_direction(lower_filename)
        if d is not None:
            return d
        return None
    else:
        for d in normal_dirs:
            if d in lower_filename:
                return d
        for part in lower_parts:
            for d in normal_dirs:
                if d in part:
                    return d
        return None

def extract_index_from_filename(filename):
    m = re.search(r'_(\d+)\.csv$', filename)
    if m:
        return int(m.group(1))
    return None

files_dict = {}  # (category, direction): [(old_file_full_path, old_index), ...]

# 扫描原目录，收集文件
for root, dirs, files in os.walk(original_root):
    for f in files:
        if f.lower().endswith(".csv"):
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, original_root)
            path_parts = rel_path.split(os.sep)
            
            category = find_category_in_path(path_parts)
            if category is None:
                print(f"Skipped file {full_path}: cannot determine category")
                continue
            
            direction = find_direction(category, path_parts, f)
            if direction is None:
                print(f"Skipped file {full_path}: cannot determine direction")
                continue
            
            old_index = extract_index_from_filename(f)
            key = (category, direction)
            if key not in files_dict:
                files_dict[key] = []
            files_dict[key].append((full_path, old_index))

# 创建new_root目录（如不存在）
os.makedirs(new_root, exist_ok=True)

mapping_file_path = os.path.join(new_root, "mapping.txt")
with open(mapping_file_path, "w", encoding="utf-8") as mapping_file:
    # 创建新目录并复制
    for (cat, dirc), file_list in files_dict.items():
        file_list.sort(key=lambda x: x[0])  # 按旧路径排序
        out_dir = os.path.join(new_root, cat, dirc)
        os.makedirs(out_dir, exist_ok=True)
        
        for new_index, (old_file, _) in enumerate(file_list):
            new_filename = f"{dirc}_{new_index}.csv"
            new_path = os.path.join(out_dir, new_filename)
            shutil.copy2(old_file, new_path)
            print(f"Copied {old_file} -> {new_path}")
            mapping_file.write(f"{old_file} -> {new_path}\n")
