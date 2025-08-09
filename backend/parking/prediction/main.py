import pandas as pd
import json
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from datetime import datetime
import os
import joblib

class ParkingPredictor:
    def __init__(self):
        self.model = LogisticRegression()

    def preprocess(self, data):
        # Extract hour from status_timestamp
        data['hour'] = data['status_timestamp'].apply(
            lambda x: datetime.fromisoformat(x.split('+')[0]).hour
        )
        # Select features
        X = data[['zone_number', 'kerbsideid', 'hour']]
        # Target: 1 if Unoccupied, 0 otherwise
        y = data['status_description'].apply(
            lambda x: 1 if x.lower() == 'unoccupied' else 0
        )
        # Drop rows with NaN values in features
        mask = X.notnull().all(axis=1)
        X = X[mask]
        y = y[mask]
        return X, y

    def train(self, data):
        X, y = self.preprocess(data)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.model.fit(X_train, y_train)
        print(f"Training accuracy: {self.model.score(X_test, y_test):.2f}")

    def predict_proba(self, zone_number, kerbsideid, dt):
        hour = datetime.fromisoformat(dt.split('+')[0]).hour
        X_pred = pd.DataFrame(
            [[zone_number, kerbsideid, hour]],
            columns=['zone_number', 'kerbsideid', 'hour']
        )
        return self.model.predict_proba(X_pred)

    def save(self, path):
        joblib.dump(self.model, path)
        print(f"Model saved to {path}")

    def load(self, path):
        self.model = joblib.load(path)
        print(f"Model loaded from {path}")

if __name__ == "__main__":
    # Load data.json from the same directory
    data_path = os.path.join(os.path.dirname(__file__), 'data.json')
    with open(data_path, 'r') as f:
        raw_data = json.load(f)
    data = pd.DataFrame(raw_data)
    predictor = ParkingPredictor()
    predictor.train(data)
    # Save the model
    model_path = os.path.join(os.path.dirname(__file__), 'parking_model.joblib')
    predictor.save(model_path)
    # Example: Load and predict
    predictor.load(model_path)
    zone_number = 7303
    kerbsideid = 51614
    dt = "2025-03-25T11:44:37+11:00"
    print("Probability:", predictor.predict_proba(zone_number, kerbsideid, dt))  # Example prediction