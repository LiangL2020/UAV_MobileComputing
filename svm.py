# Required packages
import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report
from glob import glob

# Function to load and filter CSV data
def load_and_filter_csv(file_path, max_timestamp=3):
    df = pd.read_csv(file_path)
    # Filter rows where the timestamp is <= max_timestamp
    df_filtered = df[df['timestamp'] <= max_timestamp].iloc[:, 1:]  # Exclude the timestamp column
    return df_filtered.values.flatten()  # Flatten the matrix into a single array

# Prepare data and labels with full class labels
features_list = []
labels_list = []
label_mapping = {}
label_counter = 0

# Path to the extracted data folder
extracted_folder_path = 'C:\\Users\\lenovo\\Downloads\\data'

# Load data, filter by timestamp, and prepare for SVM with specific labels
for file in glob(f"{extracted_folder_path}\\*\\*.csv"):

    # Construct the full label using directory structure and file name
    action_category =  file.split("\\")[-2]# e.g., 'tilted'
    direction = file.split("\\")[-1].split('_')[0]  # e.g., 'up' from 'up_4.csv'
    action_direction_label = f"{action_category}_{direction}"
    print(action_direction_label)

    # Assign a numerical label if not already present
    if action_direction_label not in label_mapping:
        label_mapping[action_direction_label] = label_counter
        label_counter += 1

    # Load and process the CSV file
    file_path = file
    df = pd.read_csv(file_path)
    df_filtered = df.iloc[:120, 1:]  # Filter based on timestamp and exclude the timestamp column
    features = df_filtered.values.flatten()  # Flatten the filtered matrix

    features_list.append(features)  # Keep rows where the first column is <= 3
    labels_list.append(label_mapping[action_direction_label])
# # Ensure all feature arrays are the same length by padding with zeros if necessary
# max_length = max(len(f) for f in features_list)
# features_list = [f for f in features_list]

# Convert to numpy arrays
X = np.array(features_list)
y = np.array(labels_list)
print(X.shape,y.shape)
# Split data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Standardize the data
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Train an SVM classifier
svm_classifier = SVC(kernel='linear', random_state=42)
svm_classifier.fit(X_train, y_train)

# Predict and evaluate the model
y_pred = svm_classifier.predict(X_test)
print(y_pred)
print(y_test)
report = classification_report(
    y_test,
    y_pred,
    target_names=list(label_mapping.keys()),
    labels=list(label_mapping.values()),
    zero_division=0
)
# Display the report and label mapping
print(report)
print("Label Mapping:", label_mapping)
