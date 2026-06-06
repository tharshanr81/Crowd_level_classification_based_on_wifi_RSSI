import pandas as pd
import numpy as np
import scipy.stats
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import os

# --- Configuration ---
WINDOW_SIZE = 10  # How many RSSI samples to look at? (10 samples * 0.5s/sample = 5s window)
STEP_SIZE = 5     # How many samples to slide the window? (5 samples = 2.5s)

# File names for your labeled data
DATA_FILES = {
    "low": "low_crowd.csv",
    "medium": "medium_crowd.csv",
    "high": "high_crowd.csv"
}

def generate_dummy_data_if_needed():
    """Checks if data files exist. If not, creates fake data."""
    for label, filename in DATA_FILES.items():
        if not os.path.exists(filename):
            print(f"Warning: File '{filename}' not found. Generating dummy data.")
            num_samples = 1000
            if label == "low":
           
                base_rssi = -50
                noise = np.random.normal(0, 0.5, num_samples) # Low variance
            elif label == "medium":
                # Medium crowd = some fluctuation
                base_rssi = -55
                noise = np.random.normal(0, 2.0, num_samples) # Medium variance
            else: # high
                # High crowd = high fluctuation
                base_rssi = -60
                noise = np.random.normal(0, 4.0, num_samples) # High variance
            
            timestamps = np.arange(num_samples)
            rssi_values = base_rssi + noise
            df = pd.DataFrame({"timestamp": timestamps, "rssi": rssi_values})
            df.to_csv(filename, index=False)
            print(f"Created dummy file: {filename}")


# --- 2. Feature Engineering ---
def extract_features(window_data):
    """
    Calculates statistical features from a window of RSSI data.
    This is the most important part of the project.
    """
    rssi = window_data['rssi']
    
    # Check if window is empty
    if rssi.empty:
        return [0, 0, 0, 0, 0] # Return zeros or handle as needed

    features = [
        np.mean(rssi),
        np.var(rssi),
        np.std(rssi),
        np.min(rssi),
        np.max(rssi),
        scipy.stats.iqr(rssi) # Interquartile Range (robust to outliers)
    ]
    return features

# Define names for our features
FEATURE_NAMES = ["mean", "variance", "std", "min", "max", "iqr"]


# --- 3. Data Loading and Processing ---
def load_and_process_data(filepath, label):
    """Loads a CSV, slides a window, extracts features, and assigns a label."""
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return pd.DataFrame(), []
        
    all_features = []
    
    # Slide a window over the data
    for i in range(0, len(df) - WINDOW_SIZE, STEP_SIZE):
        window = df.iloc[i : i + WINDOW_SIZE]
        features = extract_features(window)
        all_features.append(features)
        
    # Create a DataFrame with the features
    feature_df = pd.DataFrame(all_features, columns=FEATURE_NAMES)
    # Create the labels
    labels = [label] * len(feature_df)
    
    return feature_df, labels


# --- 4. Main Training Pipeline ---
def train_model():
    print("Starting model training pipeline...")
    
    # Generate dummy data if real data is missing
    generate_dummy_data_if_needed()
    
    all_feature_dfs = []
    all_labels_list = []
    
    # Load and process each data file
    for label, filename in DATA_FILES.items():
        print(f"Processing {filename} for label '{label}'...")
        feature_df, labels = load_and_process_data(filename, label)
        all_feature_dfs.append(feature_df)
        all_labels_list.extend(labels)
        
    # Combine all data into one big DataFrame
    X = pd.concat(all_feature_dfs).reset_index(drop=True)
    y = pd.Series(all_labels_list)
    
    # Handle potential NaNs (from empty windows, etc.)
    X = X.fillna(0)
    
    if X.empty:
        print("Error: No data to train on. Exiting.")
        return

    print(f"\nTotal windows created: {len(X)}")
    print(f"Label distribution:\n{y.value_counts()}")
    
    # Split data into training and testing sets (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # --- 5. Model Training (Random Forest) ---
    print("\nTraining the Random Forest Classifier...")
    # We use RandomForest because it's powerful and good with this type of data
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # --- 6. Model Evaluation ---
    print("\nModel Evaluation:")
    y_pred = model.predict(X_test)
    
    print("Classification Report:")
    print(classification_report(y_test, y_pred))
    
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred, labels=["low", "medium", "high"]))
    
    # --- 7. Save the Model ---
    model_filename = "crowd_model.pkl"
    joblib.dump(model, model_filename)
    print(f"\nModel successfully trained and saved as '{model_filename}'")

    
# --- 8. Real-Time Prediction Function (This is what you use in your app) ---
def predict_crowd_level(live_rssi_window_data):
    """
    Predicts the crowd level from a new window of RSSI data.
    'live_rssi_window_data' should be a list or array of RSSI values
    (length = WINDOW_SIZE).
    """
    try:
        # 1. Load the trained model
        model = joblib.load("crowd_model.pkl")
    except FileNotFoundError:
        print("Error: Model file 'crowd_model.pkl' not found.")
        print("Please run the training script first.")
        return None
        
    # 2. Wrap data in a dummy DataFrame to use our feature extractor
    live_df = pd.DataFrame({"rssi": live_rssi_window_data})
    
    # 3. Extract the *exact same* features as during training
    features = extract_features(live_df)
    
    # 4. Reshape features for a single prediction
    # The model expects a 2D array, so we wrap our 1D features in []
    features_2d = [features]
    
    # 5. Make the prediction
    prediction = model.predict(features_2d)
    
    return prediction[0] # Return the first (and only) prediction


# --- Main execution ---
if __name__ == "__main__":
    # 1. Train the model
    train_model()
    
    # 2. Example of a live prediction
    print("\n--- Live Prediction Example ---")
    
    # Create a fake "live" window of RSSI data with high variance
    # (Should be classified as "high")
    fake_live_data = np.random.normal(-60, 4.0, WINDOW_SIZE)
    
    predicted_level = predict_crowd_level(fake_live_data)
    
    if predicted_level:
        print(f"Live data window: {fake_live_data.round(1)}")
        print(f"==> Predicted Crowd Level: {predicted_level.upper()}")