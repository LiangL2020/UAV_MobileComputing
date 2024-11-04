import numpy as np
import pandas as pd
from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Load data function
def load_data(file_path):
    """
    Loads data from a CSV file. Assumes the last column is the label.
    """
    data = pd.read_csv(file_path)
    X = data.iloc[:, :-1].values  # Features (N*6 vectors)
    y = data.iloc[:, -1].values   # Labels
    return X, y

# Load dataset
file_path = 'dataset.csv'  # Replace with your dataset path
X, y = load_data(file_path)

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Train the SVM classifier
clf = svm.SVC(kernel='linear', C=1.0)  # You can change the kernel as needed
clf.fit(X_train, y_train)

# Make predictions on the test set
y_pred = clf.predict(X_test)

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {accuracy:.2f}")

# Inference function
def predict_new_samples(model, new_samples):
    """
    Predicts the labels for new samples using the trained model.
    """
    predictions = model.predict(new_samples)
    return predictions

# Example of inference
new_samples = np.array([[1.5, 2.3, 3.1, 4.0, 5.2, 6.1],   # Replace with actual sample vectors
                        [7.2, 8.3, 9.1, 1.0, 0.2, 3.3]])
predicted_labels = predict_new_samples(clf, new_samples)
print("Predicted labels for new samples:", predicted_labels)
