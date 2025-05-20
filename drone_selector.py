# drone_selector.py

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import NearestNeighbors
import skfuzzy as fuzz

# Constants
CATEGORICAL_FEATURES = [
    "Thermal/Night Camera",
    "Real-time data transmission",
    "Air/Water quality sensor availability",
    "Automatic Landing/Takeoff",
    "Automated Path Finding"
]

TEXTUAL_FEATURES = [
    "Camera Quality",
    "Class Identification Label",
    "GPS Supported Systems"
]

# Fuzzy membership functions for selected features
def fuzzy_membership_payload(x):
    # Define fuzzy sets: low, medium, high
    low = fuzz.trimf(x, [0, 0, 10])
    medium = fuzz.trimf(x, [5, 15, 25])
    high = fuzz.trimf(x, [20, 30, 30])
    return {"low": low, "medium": medium, "high": high}


def preprocess_data(df):
    df_processed = df.copy()

    # Encode Camera Quality ordinally
    quality_map = {"480p": 1, "720p": 2, "1080p": 3, "4K": 4, "6K": 5}
    df_processed["Camera Quality"] = df_processed["Camera Quality"].map(quality_map)

    # One-hot encode Class ID and GPS Systems
    df_processed = pd.get_dummies(df_processed, columns=[
        "Class Identification Label",
        "GPS Supported Systems"
    ])

    return df_processed


def scale_features(df, user_input):
    scaler = MinMaxScaler()
    df_scaled = df.copy()

    # Get all features except Drone ID
    features = [col for col in df.columns if col != "Drone ID"]

    # Process user input
    user_df = pd.DataFrame([user_input])
    user_df = preprocess_data(user_df)

    # Add missing columns to user_df (from df)
    for col in df.columns:
        if col not in user_df.columns:
            user_df[col] = 0

    # Ensure same column order
    user_df = user_df[df.columns]

    # Scale
    df_scaled[features] = scaler.fit_transform(df_scaled[features])
    user_scaled = scaler.transform(user_df[features])

    return df_scaled, user_scaled[0]


def compute_fuzzy_score(drone, user_input, weights):
    score = 0
    explanations = []

    # Example fuzzy comparison: Payload Capacity
    payload_membership = fuzzy_membership_payload(np.array([drone["Payload Capacity"]]))

    desired = user_input["Payload Capacity"]
    if desired <= 10:
        relevance = payload_membership["low"][0]
        label = "low"
    elif desired <= 20:
        relevance = payload_membership["medium"][0]
        label = "medium"
    else:
        relevance = payload_membership["high"][0]
        label = "high"

    score += weights["Payload Capacity"] * relevance
    explanations.append(f"Payload matches '{label}' category with weight {weights['Payload Capacity']:.2f}.")

    # Add more fuzzy evaluations here if needed
    return score, explanations



def get_top_drones(user_input_gui, weights_gui, k=3):
    df = pd.read_csv("drones_dataset.csv")
    df_processed = preprocess_data(df)
    df_scaled, user_scaled = scale_features(df_processed, user_input_gui)

    # Fit Nearest Neighbors model
    features = [col for col in df_scaled.columns if col not in ["Drone ID"]]
    model = NearestNeighbors(n_neighbors=k, metric="euclidean")
    model.fit(df_scaled[features])
    user_df_scaled = pd.DataFrame([user_scaled], columns=features)
    distances, indices = model.kneighbors(user_df_scaled)

    max_dist = np.linalg.norm(np.ones(len(features)))  # max possible distance in normalized space

    top_drones = []
    for dist, idx in zip(distances[0], indices[0]):
        drone_row = df.iloc[idx].copy()
        fuzzy_score, explanations = compute_fuzzy_score(drone_row, user_input_gui, weights_gui)

        # Normalize distance score
        norm_dist_score = max(0.0, 1 - dist / max_dist)  # clamp to 0

        # Combine with fuzzy logic (weights can be changed)
        total_score = (norm_dist_score * 0.5 + fuzzy_score * 0.5) * 100  # percent

        top_drones.append({
            "Drone ID": drone_row["Drone ID"],
            "Total Score (%)": round(total_score, 2),
            "Price": drone_row["Budgets options"],
            "Explanation": explanations
        })

    # Sort by final score
    top_drones.sort(key=lambda x: x["Total Score (%)"], reverse=True)

    return top_drones

if __name__ == "__main__":
    # Example usage
    user_input = {
        "Flight Radius": 7.0,
        "Flight height": 300.0,
        "Thermal/Night Camera": 1,
        "Max wind resistance": 10.0,
        "Budgets options": 8000.0,
        "Camera Quality": "1080p",
        "ISO range": 3200,
        "Battery Life": 90.0,
        "Payload Capacity": 15.0,
        "Dimensions": 3000.0,
        "Real-time data transmission": 1,
        "Transmission bandwidth": 50.0,
        "Data storage ability": 128,
        "Air/Water quality sensor availability": 1,
        "Noise level": 50.0,
        "Operating Temperature": 20.0,
        "Class Identification Label": "C2",
        "Charging Time": 60.0,
        "Automatic Landing/Takeoff": 1,
        "GPS Supported Systems": "GPS+Galileo",
        "Automated Path Finding": 1
    }

    weights = {
        "Payload Capacity": 0.7,
        # Add weights for other features if fuzzy logic is extended
    }

    result = get_top_drones(user_input, weights)
    for drone in result:
        print(f"\nDrone ID: {drone['Drone ID']}")
        print(f"Total Score: {drone['Total Score (%)']}%")
        for expl in drone["Explanation"]:
            print("-", expl)
