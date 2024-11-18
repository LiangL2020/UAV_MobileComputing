# Required packages
import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report
import lightgbm as lgb
from glob import glob

# Function to load and filter CSV data
def load_and_filter_csv(file_path, max_timestamp=3):
    df = pd.read_csv(file_path)
    # Filter rows where the timestamp is <= max_timestamp
    df_filtered = df[df['timestamp'] <= max_timestamp].iloc[:, 1:]  # Exclude the timestamp column
    return df_filtered.values.flatten()  # Flatten the matrix into a single array

# Function to add Gaussian noise to data
def add_gaussian_noise(X, mean=0, std=0.01):
    noise = np.random.normal(mean, std, X.shape)
    return X + noise

# Prepare data and labels with full class labels
features_list = []
labels_list = []
label_mapping = {}
label_counter = 0

# Path to the extracted data folder
extracted_folder_path = 'C:\\Users\\lenovo\\Downloads\\data'

# Load data, filter by timestamp, and prepare for training with specific labels
for file in glob(f"{extracted_folder_path}\\*\\*.csv"):
    # Construct the full label using directory structure and file name
    action_category = file.split("\\")[-2]  # e.g., 'tilted'
    direction = file.split("\\")[-1].split('_')[0]  # e.g., 'up' from 'up_4.csv'
    action_direction_label = f"{action_category}_{direction}"

    # Assign a numerical label if not already present
    if action_direction_label not in label_mapping:
        label_mapping[action_direction_label] = label_counter
        label_counter += 1

    # Load and process the CSV file
    file_path = file
    df = pd.read_csv(file_path)
    df_filtered = df.iloc[:120, 1:]  # Truncate to the first 120 rows and exclude the timestamp column
    features = df_filtered.values.flatten()  # Flatten the filtered matrix

    features_list.append(features)
    labels_list.append(label_mapping[action_direction_label])

# Convert to numpy arrays
X = np.array(features_list)
y = np.array(labels_list)

# Split data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Normalize features by subtracting mean and dividing by standard deviation
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Augment training data (optional, set flag to False to skip)
augment_train = True
if augment_train:
    X_train_augmented = add_gaussian_noise(X_train, std=0.01)
    X_train_combined = np.vstack([X_train, X_train_augmented])
    y_train_combined = np.hstack([y_train, y_train])
else:
    X_train_combined = X_train
    y_train_combined = y_train

# Train a LightGBM model
lgb_train = lgb.Dataset(X_train_combined, label=y_train_combined)
lgb_params = {
    'objective': 'multiclass',
    'num_class': len(label_mapping),
    'metric': 'multi_logloss',
    'boosting_type': 'gbdt',
    'num_leaves': 31,
    'learning_rate': 0.05,
    'feature_fraction': 0.9
}
lgb_model = lgb.train(lgb_params, lgb_train, num_boost_round=100)

# Predict and evaluate the model on the test set
y_pred = lgb_model.predict(X_test)
y_pred_labels = np.argmax(y_pred, axis=1)
print(y_pred_labels)
print(y_test)
report = classification_report(
    y_test,
    y_pred_labels,
    target_names=list(label_mapping.keys()),
    labels=list(label_mapping.values()),
    zero_division=0
)

# Display the report and label mapping
print(report)
print("Label Mapping:", label_mapping)
