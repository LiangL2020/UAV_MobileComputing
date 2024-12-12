import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

data_root = "data_new"  # 存放 category/direction/... 数据的根目录
output_csv = "combined_data.csv"

categories = ["curved", "straight", "tilted", "rotate"]
normal_dirs = ["up","down","left","right"]
rotate_dirs = ["cw", "ccw"]  # rotate下的方向

# 按题意，共14类
class_list = [
    "curved_up", "curved_down", "curved_left", "curved_right",
    "straight_up", "straight_down", "straight_left", "straight_right",
    "tilted_up", "tilted_down", "tilted_left", "tilted_right",
    "rotate_cw", "rotate_ccw"
]
label_to_id = {label: idx for idx, label in enumerate(class_list)}

def get_label(category, direction):
    return f"{category}_{direction}"

file_list = []
for cat in categories:
    cat_dir = os.path.join(data_root, cat)
    if not os.path.isdir(cat_dir):
        continue
    if cat == "rotate":
        possible_dirs = rotate_dirs
    else:
        possible_dirs = normal_dirs
    
    for d in possible_dirs:
        d_dir = os.path.join(cat_dir, d)
        if not os.path.isdir(d_dir):
            continue
        for f in os.listdir(d_dir):
            if f.lower().endswith(".csv"):
                file_path = os.path.join(d_dir, f)
                label_str = get_label(cat, d)
                if label_str not in label_to_id:
                    print(f"Warning: {label_str} not in label_to_id mapping, skipping.")
                    continue
                file_list.append((file_path, label_to_id[label_str]))

row_counts = []
data_arrays = []
labels = []
for fpath, label_id in file_list:
    # 使用header=0来表示第一行为表头，不作为数据行
    df = pd.read_csv(fpath, header=0)
    # 确保列数量正确（原本7列：1列timestamp + 6列特征）
    if df.shape[1] != 7:
        print(f"Warning: {fpath} does not have 7 columns after reading header, skipping.")
        continue
    # 忽略第一列(timestamp)
    data = df.iloc[:,1:].values
    if data.shape[1] != 6:
        print(f"Warning: {fpath} after ignoring the first column does not have 6 columns, skipping.")
        continue
    row_counts.append(data.shape[0])
    data_arrays.append(data)
    labels.append(label_id)

if len(row_counts) == 0:
    raise ValueError("No valid files found.")

min_n = min(row_counts)

# 截断并展开
truncated_data = []
for arr in data_arrays:
    truncated = arr[:min_n, :]
    truncated_flat = truncated.flatten()
    truncated_data.append(truncated_flat)

X = np.array(truncated_data)
y = np.array(labels)

# min-max normalization
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)

# 保存到CSV（标签列使用整数ID）
df_out = pd.DataFrame(X_scaled)
df_out['label'] = y
df_out.to_csv(os.path.join(data_root, output_csv), index=False)
print(f"Combined dataset saved to {os.path.join(data_root, output_csv)}")

# 简单训练测试划分
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, stratify=y)

clf = RandomForestClassifier(random_state=42)
clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)
subset_labels = [0, 5, 6, 7, 9, 10, 11]
subset_class_names = [class_list[i] for i in subset_labels] 
print(classification_report(y_test, y_pred, labels=subset_labels,target_names=subset_class_names))
