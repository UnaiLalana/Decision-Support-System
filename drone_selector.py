# drone_selector.py

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import NearestNeighbors
import skfuzzy as fuzz
from skfuzzy import control as ctrl  # For a more structured definition, although we'll use simple trimf for now

# Constants
CATEGORICAL_FEATURES = [  # Assume these are already 0/1 or handled as such
    "Thermal/Night Camera",
    "Real-time data transmission",
    "Air/Water quality sensor availability",
    "Automatic Landing/Takeoff",
    "Automated Path Finding"
]

TEXTUAL_FEATURES = [  # Features requiring specific pre-processing
    "Camera Quality",  # Ordinal
    "Class Identification Label",  # Nominal -> One-hot
    "GPS Supported Systems"  # Nominal -> One-hot
]


# --- Fuzzy membership functions ---
def fuzzy_membership_payload(x):  # Higher values are better
    # x is a numpy array of drone payload capacity values
    low = fuzz.trimf(x, [0, 0, 5])       # Less than 5kg is low
    medium = fuzz.trimf(x, [3, 10, 15])  # Between 3kg and 15kg is medium
    high = fuzz.trimf(x, [12, 25, 40])   # Above 12kg (up to 40) is high
    return {"low": low, "medium": medium, "high": high}


def fuzzy_membership_budget(x):  # Lower values are better
    # x is a numpy array of drone prices
    affordable = fuzz.trimf(x, [0, 0, 5000])       # Below 5000 is affordable
    moderate = fuzz.trimf(x, [4000, 7500, 10000])  # Between 4000 and 10000 is moderate
    expensive = fuzz.trimf(x, [8000, 15000, 30000])# Above 8000 (up to 30000) is expensive
    return {"affordable": affordable, "moderate": moderate, "expensive": expensive}


def fuzzy_membership_battery(x):  # Higher values are better
    # x is a numpy array of drone battery life (in minutes)
    short = fuzz.trimf(x, [0, 0, 45])      # Less than 45 min is short
    medium = fuzz.trimf(x, [30, 60, 90])   # Between 30 and 90 min is medium
    long = fuzz.trimf(x, [75, 120, 180])   # Above 75 min (up to 180) is long
    return {"short": short, "medium": medium, "long": long}


# --- Data Preprocessing ---
def preprocess_data(df):
    df_processed = df.copy()

    # Ordinal map for Camera Quality
    quality_map = {"480p": 1, "720p": 2, "1080p": 3, "4K": 4, "6K": 5, "8K": 6}  # Extended for generality
    # Handle possible missing or unmapped values by assigning a default (e.g., the lowest)
    df_processed["Camera Quality"] = df_processed["Camera Quality"].map(quality_map).fillna(1)

    # One-hot encode for nominal features defined in TEXTUAL_FEATURES
    # Ensure columns exist before attempting one-hot encoding
    # This is important if the CSV might not always have all columns.
    one_hot_cols = []
    if "Class Identification Label" in df_processed.columns:
        one_hot_cols.append("Class Identification Label")
    if "GPS Supported Systems" in df_processed.columns:
        one_hot_cols.append("GPS Supported Systems")

    if one_hot_cols:
        df_processed = pd.get_dummies(df_processed, columns=one_hot_cols,
                                      dummy_na=False)  # dummy_na=False to avoid creating _nan columns

    # Force numeric conversion for columns that should be numeric
    # (e.g. after one-hot encoding or if read as object but are numeric)
    for col in df_processed.columns:
        if col != "Drone ID":  # Exclude the ID
            # Attempt numeric conversion, errors become NaN
            df_processed[col] = pd.to_numeric(df_processed[col], errors='coerce')

    # Handling NaNs post-conversion (e.g., with mean, median, or 0)
    # For simplicity, we use 0 here, but a more sophisticated strategy might be necessary
    df_processed = df_processed.fillna(0)

    return df_processed


def scale_features(df_processed, user_input_processed):
    scaler = MinMaxScaler()
    df_scaled = df_processed.copy()

    # Features to scale (all except Drone ID)
    features_to_scale = [col for col in df_processed.columns if col != "Drone ID"]

    # Ensure user_input_processed has the same columns as df_processed (except Drone ID)
    # and in the same order, for scaler.transform.
    user_input_df = pd.DataFrame([user_input_processed])

    # Column alignment: Add missing columns to user_input_df and reorder
    for col in features_to_scale:
        if col not in user_input_df.columns:
            user_input_df[col] = 0  # Default for features not specified by the user but present in the dataset
    user_input_df = user_input_df[features_to_scale]  # Reorder and select

    # Scaling
    df_scaled[features_to_scale] = scaler.fit_transform(df_processed[features_to_scale])
    user_scaled_vector = scaler.transform(user_input_df[features_to_scale])[0]

    return df_scaled, user_scaled_vector, features_to_scale, scaler


# --- Prepare Weights for k-NN ---
def prepare_knn_weights(knn_feature_names, original_user_input_keys, weights_gui):
    feature_weights = np.ones(len(knn_feature_names))  # Default weight = 1

    # Map original user input keys (in weights_gui)
    # to the actual columns used by k-NN (knn_feature_names),
    # especially for one-hot-encoded ones.
    one_hot_original_features = ["Class Identification Label", "GPS Supported Systems"]

    for i, col_name in enumerate(knn_feature_names):
        assigned_weight = False
        # Case 1: The k-NN column name is directly a key in weights_gui
        if col_name in weights_gui:
            feature_weights[i] = weights_gui[col_name]
            assigned_weight = True
        else:
            # Case 2: The k-NN column name derives from a one-hot-encoded feature
            for original_feature in one_hot_original_features:
                if col_name.startswith(original_feature + "_"):
                    if original_feature in weights_gui:
                        feature_weights[i] = weights_gui[original_feature]
                        assigned_weight = True
                        break
            # If no specific weight was assigned and it's not a derived weighted column,
            # it could be a numeric/binary feature not explicitly in weights_gui
            # or a derived column whose original feature has no weight. Keeps default 1.
            # Initialization to np.ones() already handles this, but can be made more explicit.
            if not assigned_weight and col_name not in original_user_input_keys and not any(
                    col_name.startswith(ohf + "_") for ohf in one_hot_original_features):
                # This case covers generated columns (e.g. from unmapped get_dummies) that may not have a direct weight.
                # Keep 1.0 or assign 0.0 if they should not influence. For now, 1.0.
                pass

    return feature_weights


# --- Detailed Fuzzy Scoring and Explanations ---
def compute_detailed_scores_and_explanations(drone_row, user_input_gui, weights_gui):
    total_detailed_score = 0
    total_weights_for_detailed_score = 0
    explanations = []

    # 1. Payload Capacity (higher is better for the user)
    if "Payload Capacity" in user_input_gui and "Payload Capacity" in drone_row and "Payload Capacity" in weights_gui:
        payload_val_drone = drone_row["Payload Capacity"]
        payload_val_user = user_input_gui["Payload Capacity"]
        weight = weights_gui["Payload Capacity"]

        fm_payload = fuzzy_membership_payload(np.array([payload_val_drone]))

        # ... [logic unchanged] ...

    # 2. Budget (lower is better for the user)
    if "Budgets options" in user_input_gui and "Budgets options" in drone_row and "Budgets options" in weights_gui:
        # ... [logic unchanged] ...
        pass

    # 3. Battery Life (higher is better for the user)
    if "Battery Life" in user_input_gui and "Battery Life" in drone_row and "Battery Life" in weights_gui:
        # ... [logic unchanged] ...
        pass

    # Normalize the total detailed score
    normalized_detailed_score = 0
    if total_weights_for_detailed_score > 0:
        normalized_detailed_score = total_detailed_score / total_weights_for_detailed_score

    return normalized_detailed_score, explanations


# --- Main Drone Selection Function ---
def get_top_drones(user_input_gui, weights_gui, k=3, W_knn=0.6, W_detailed=0.4):
    df = pd.read_csv("drones_dataset.csv")

    # Prepare user input (simulating the preprocessing that would also happen on the dataset)
    user_input_df_temp = pd.DataFrame([user_input_gui])
    user_input_processed = preprocess_data(user_input_df_temp).iloc[0].to_dict()

    df_processed = preprocess_data(df)
    df_scaled, user_scaled_knn_vector, knn_feature_names, scaler = scale_features(df_processed, user_input_processed)

    # 1. Weighted k-NN
    # Prepare weights for k-NN features
    knn_weights_array = prepare_knn_weights(knn_feature_names, user_input_gui.keys(), weights_gui)
    sqrt_knn_weights = np.sqrt(knn_weights_array)

    # Apply weights to the scaled features
    df_weighted_scaled_features = df_scaled[knn_feature_names] * sqrt_knn_weights
    user_weighted_scaled_vector = user_scaled_knn_vector * sqrt_knn_weights

    model = NearestNeighbors(n_neighbors=min(k, len(df_weighted_scaled_features)), metric="euclidean")
    model.fit(df_weighted_scaled_features)

    distances, indices = model.kneighbors(user_weighted_scaled_vector.reshape(1, -1))

    # Max possible distance in the weighted and scaled space (between zero vector and one vector, both weighted)
    # If a feature has weight 0, it does not contribute to max_dist.
    # A vector of ones (max scaled value) weighted with sqrt_weights.
    max_possible_weighted_scaled_vector = np.ones(len(knn_feature_names)) * sqrt_knn_weights
    max_dist = np.linalg.norm(max_possible_weighted_scaled_vector)
    if max_dist == 0: max_dist = 1  # Avoid division by zero if all weights are 0

    top_drones_data = []
    for dist, idx in zip(distances[0], indices[0]):
        drone_original_row = df.iloc[idx].copy()  # Original row for values and explanations

        # Normalized KNN score (similarity)
        # Lower distance means higher score.
        knn_similarity_score = max(0.0, 1 - (dist / max_dist)) if max_dist > 0 else 0.0

        # 2. Detailed Score (Fuzzy for Payload, Budget, Battery)
        detailed_score, fuzzy_explanations = compute_detailed_scores_and_explanations(
            drone_original_row, user_input_gui, weights_gui
        )

        # 3. Combined Total Score
        total_score = (knn_similarity_score * W_knn + detailed_score * W_detailed) * 100

        # 4. Additional General Explanations
        general_explanations = []
        for feature_name, user_value in user_input_gui.items():
            if feature_name in ["Payload Capacity", "Budgets options", "Battery Life"]:
                continue

            drone_actual_value = drone_original_row.get(feature_name, "N/A")
            weight = weights_gui.get(feature_name, 0.0)

            match_info = ""
            if pd.api.types.is_numeric_dtype(type(user_value)) and pd.api.types.is_numeric_dtype(
                    type(drone_actual_value)):
                if drone_actual_value > user_value:
                    match_info = "(Drone exceeds requirement)"
                elif drone_actual_value < user_value:
                    match_info = "(Drone below requirement)"
                else:
                    match_info = "(Exact match)"
            elif user_value == drone_actual_value:
                match_info = "(Match)"
            else:
                match_info = "(Does not match)"

            general_explanations.append(
                f"{feature_name}: Requested '{user_value}', Drone '{drone_actual_value}' {match_info}. (Weight: {weight:.2f})"
            )

        all_explanations = fuzzy_explanations + general_explanations

        top_drones_data.append({
            "Drone ID": drone_original_row["Drone ID"],
            "Total Score (%)": round(total_score, 2),
            "Price": drone_original_row.get("Budgets options", "N/A"),  # Ensure it exists
            "Explanation": all_explanations,
            "_knn_dist": dist,
            "_knn_score": round(knn_similarity_score, 3),
            "_detailed_score": round(detailed_score, 3),
        })

    # Sort by final score
    top_drones_data.sort(key=lambda x: x["Total Score (%)"], reverse=True)

    return top_drones_data


if __name__ == "__main__":
    # Example usage
    user_input = {
        "Flight Radius": 7.0,            # km
        "Flight height": 300.0,          # m
        "Thermal/Night Camera": 1,       # 0 or 1
        "Max wind resistance": 10.0,      # m/s
        "Budgets options": 8000.0,       # Max budget
        "Camera Quality": "4K",          # Text to map
        "ISO range": 3200,               # Numeric value
        "Battery Life": 90.0,            # Minutes (minimum desired)
        "Payload Capacity": 10.0,        # kg (minimum desired)
        "Dimensions": 3000.0,            # cubic mm or similar (interpreted as "max acceptable" or "desired")
        "Real-time data transmission": 1,# 0 or 1
        "Transmission bandwidth": 50.0,   # Mbps
        "Data storage ability": 128,     # GB
        "Air/Water quality sensor availability": 0, # 0 or 1
        "Noise level": 50.0,             # dB (lower is better, k-NN will treat as "closer is better")
        "Operating Temperature": 20.0,   # Celsius (desired value, k-NN "closer is better")
        "Class Identification Label": "C2", # Text -> one-hot
        "Charging Time": 60.0,           # Minutes (lower is better, k-NN "closer is better")
        "Automatic Landing/Takeoff": 1,   # 0 or 1
        "GPS Supported Systems": "GPS+Galileo", # Text -> one-hot
        "Automated Path Finding": 1       # 0 or 1
    }

    # Weights for each user input feature
    # Higher values indicate greater importance. A weight of 0 excludes the feature from influence (or almost, if the default is small).
    # A weight of 1.0 is neutral if the default is 1.0.
    weights = {
        "Flight Radius": 1.5,
        "Flight height": 0.8,
        "Thermal/Night Camera": 2.0,
        "Max wind resistance": 1.2,
        "Budgets options": 2.5,
        "Camera Quality": 1.8,
        "ISO range": 0.7,
        "Battery Life": 2.2,
        "Payload Capacity": 2.0,
        "Dimensions": 0.5,
        "Real-time data transmission": 1.5,
        "Transmission bandwidth": 0.9,
        "Data storage ability": 1.0,
        "Air/Water quality sensor availability": 1.2,
        "Noise level": 0.6,
        "Operating Temperature": 0.7,
        "Class Identification Label": 1.8,
        "Charging Time": 0.8,
        "Automatic Landing/Takeoff": 1.3,
        "GPS Supported Systems": 1.5,
        "Automated Path Finding": 1.0
    }

    result = get_top_drones(user_input, weights, k=3, W_knn=0.6, W_detailed=0.4)

    print(f"\n--- TOP {len(result)} DRONES FOUND ---")
    for i, drone in enumerate(result):
            print(f"\n{i + 1}. Drone ID: {drone['Drone ID']}")
            print(
                f"   Total Score: {drone['Total Score (%)']}% (KNN: {drone['_knn_score']:.2f}, Detailed: {drone['_detailed_score']:.2f})")
            print(f"   Price: {drone['Price']}")
            print("   Detailed Explanations:")
            for expl in drone["Explanation"]:
                print(f"   - {expl}")

