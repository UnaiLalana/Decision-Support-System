# drone_selector.py

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import NearestNeighbors
import skfuzzy as fuzz

# from skfuzzy import control as ctrl # Not strictly needed for this direct fuzzy logic

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


# --- Fuzzy membership functions ---
def fuzzy_membership_payload(x):
    low = fuzz.trimf(x, [0, 0, 5])
    medium = fuzz.trimf(x, [3, 10, 15])
    high = fuzz.trimf(x, [12, 25, 40])
    return {"low": low, "medium": medium, "high": high}


def fuzzy_membership_budget(x):
    affordable = fuzz.trimf(x, [0, 0, 5000])
    moderate = fuzz.trimf(x, [4000, 7500, 10000])
    expensive = fuzz.trimf(x, [8000, 15000, 30000])
    return {"affordable": affordable, "moderate": moderate, "expensive": expensive}


def fuzzy_membership_battery(x):
    short = fuzz.trimf(x, [0, 0, 45])
    medium = fuzz.trimf(x, [30, 60, 90])
    long = fuzz.trimf(x, [75, 120, 180])
    return {"short": short, "medium": medium, "long": long}


# --- Data Preprocessing ---
def preprocess_data(df):
    df_processed = df.copy()
    quality_map = {"480p": 1, "720p": 2, "1080p": 3, "4K": 4, "6K": 5, "8K": 6}
    df_processed["Camera Quality"] = df_processed["Camera Quality"].map(quality_map).fillna(1)

    one_hot_cols = []
    if "Class Identification Label" in df_processed.columns:
        one_hot_cols.append("Class Identification Label")
    if "GPS Supported Systems" in df_processed.columns:
        one_hot_cols.append("GPS Supported Systems")

    if one_hot_cols:
        df_processed = pd.get_dummies(df_processed, columns=one_hot_cols, dummy_na=False)

    for col in df_processed.columns:
        if col != "Drone ID":
            df_processed[col] = pd.to_numeric(df_processed[col], errors='coerce')
    df_processed = df_processed.fillna(0)
    return df_processed


def scale_features(df_processed, user_input_processed):
    scaler = MinMaxScaler()
    df_scaled = df_processed.copy()
    features_to_scale = [col for col in df_processed.columns if col != "Drone ID"]
    user_input_df = pd.DataFrame([user_input_processed])
    for col in features_to_scale:
        if col not in user_input_df.columns:
            user_input_df[col] = 0
    user_input_df = user_input_df[features_to_scale]
    df_scaled[features_to_scale] = scaler.fit_transform(df_processed[features_to_scale])
    user_scaled_vector = scaler.transform(user_input_df[features_to_scale])[0]
    return df_scaled, user_scaled_vector, features_to_scale, scaler


# --- Prepare Weights for k-NN ---
def prepare_knn_weights(knn_feature_names, original_user_input_keys, weights_gui):
    feature_weights = np.ones(len(knn_feature_names))
    one_hot_original_features = ["Class Identification Label", "GPS Supported Systems"]
    for i, col_name in enumerate(knn_feature_names):
        assigned_weight = False
        if col_name in weights_gui:
            feature_weights[i] = weights_gui[col_name]
            assigned_weight = True
        else:
            for original_feature in one_hot_original_features:
                if col_name.startswith(original_feature + "_"):
                    if original_feature in weights_gui:
                        feature_weights[i] = weights_gui[original_feature]
                        assigned_weight = True
                        break
            if not assigned_weight and col_name not in original_user_input_keys and not any(
                    col_name.startswith(ohf + "_") for ohf in one_hot_original_features):
                pass
    return feature_weights


# --- Detailed Fuzzy Scoring and Explanations ---
def compute_detailed_scores_and_explanations(drone_row, user_input_gui, weights_gui):
    total_detailed_score = 0.0
    total_weights_for_detailed_score = 0.0  # Use float for consistency
    explanations = []

    # 1. Payload Capacity (higher is better for the user)
    if "Payload Capacity" in user_input_gui and "Payload Capacity" in drone_row and pd.notna(
            drone_row["Payload Capacity"]) and "Payload Capacity" in weights_gui:
        payload_val_drone = float(drone_row["Payload Capacity"])
        payload_val_user = float(user_input_gui["Payload Capacity"])
        weight = float(weights_gui["Payload Capacity"])

        fm_payload = fuzzy_membership_payload(np.array([payload_val_drone]))

        relevance = 0.0
        drone_category_label = ""
        # User wants AT LEAST payload_val_user.
        if payload_val_drone >= payload_val_user:  # Drone meets or exceeds requirement
            if fm_payload["high"][0] > 0.5:  # Significantly high
                relevance = fm_payload["high"][0]
                drone_category_label = "high"
            elif fm_payload["medium"][0] > 0.5:  # Significantly medium
                relevance = fm_payload["medium"][0]
                drone_category_label = "medium"
            else:  # Meets but not exceptional in high/medium categories, still good
                relevance = max(fm_payload["low"][0], fm_payload["medium"][0],
                                fm_payload["high"][0])  # Take its best fit
                if relevance == fm_payload["high"][0]:
                    drone_category_label = "high (satisfactory)"
                elif relevance == fm_payload["medium"][0]:
                    drone_category_label = "medium (satisfactory)"
                else:
                    drone_category_label = "low (satisfactory but meets min)"
        else:  # Drone is below requirement
            # Penalize, but "closeness" might still count. Assign relevance based on its category.
            if fm_payload["high"][0] > fm_payload["medium"][0] and fm_payload["high"][0] > fm_payload["low"][0]:
                relevance = fm_payload["high"][0] * 0.5  # Example penalty factor
                drone_category_label = "high (but below user requirement)"
            elif fm_payload["medium"][0] > fm_payload["low"][0]:
                relevance = fm_payload["medium"][0] * 0.5  # Example penalty factor
                drone_category_label = "medium (but below user requirement)"
            else:
                relevance = fm_payload["low"][0] * 0.5  # Example penalty factor
                drone_category_label = "low (below user requirement)"

        total_detailed_score += weight * relevance
        total_weights_for_detailed_score += weight
        explanations.append(
            f"Payload: User wants >= {payload_val_user}kg, Drone has {payload_val_drone}kg (Drone category: '{drone_category_label}')")

    # 2. Budget (lower is better for the user)
    if "Budgets options" in user_input_gui and "Budgets options" in drone_row and pd.notna(
            drone_row["Budgets options"]) and "Budgets options" in weights_gui:
        budget_val_drone = float(drone_row["Budgets options"])
        budget_val_user = float(user_input_gui["Budgets options"])  # User specifies a max budget
        weight = float(weights_gui["Budgets options"])

        fm_budget = fuzzy_membership_budget(np.array([budget_val_drone]))


        # User wants to spend AT MOST budget_val_user
        if budget_val_drone <= budget_val_user:  # Drone is within budget
            if fm_budget["affordable"][0] > 0.5:
                relevance = fm_budget["affordable"][0]
                drone_category_label = "affordable"
            elif fm_budget["moderate"][0] > 0.5:
                relevance = fm_budget["moderate"][0]
                drone_category_label = "moderate (within budget)"
            else:  # Within budget, but might be in the "expensive" fuzzy set or not strongly in affordable/moderate
                relevance = 1.0  # If within user's max, it's fully relevant for this part. Could also use its fuzzy value.
                drone_category_label = "within budget (may be 'expensive' category but meets user max)"
        else:  # Drone is over budget
            relevance = 0.0  # Strictly over budget, 0 relevance for this fuzzy criterion.
            drone_category_label = "over budget"

        total_detailed_score += weight * relevance
        total_weights_for_detailed_score += weight
        explanations.append(
            f"Budget: User wants <= {budget_val_user}, Drone costs {budget_val_drone} (Drone category: '{drone_category_label}')")

    # 3. Battery Life (higher is better for the user)
    if "Battery Life" in user_input_gui and "Battery Life" in drone_row and pd.notna(
            drone_row["Battery Life"]) and "Battery Life" in weights_gui:
        battery_val_drone = float(drone_row["Battery Life"])
        battery_val_user = float(user_input_gui["Battery Life"])  # User specifies a minimum duration
        weight = float(weights_gui["Battery Life"])

        fm_battery = fuzzy_membership_battery(np.array([battery_val_drone]))
        relevance = 0.0
        drone_category_label = ""

        if battery_val_drone >= battery_val_user:  # Drone meets or exceeds requirement
            if fm_battery["long"][0] > 0.5:
                relevance = fm_battery["long"][0]
                drone_category_label = "long"
            elif fm_battery["medium"][0] > 0.5:
                relevance = fm_battery["medium"][0]
                drone_category_label = "medium"
            else:  # Meets requirement but not exceptionally long/medium
                relevance = max(fm_battery["short"][0], fm_battery["medium"][0],
                                fm_battery["long"][0])  # Take its best fit
                if relevance == fm_battery["long"][0]:
                    drone_category_label = "long (satisfactory)"
                elif relevance == fm_battery["medium"][0]:
                    drone_category_label = "medium (satisfactory)"
                else:
                    drone_category_label = "short (satisfactory but meets min)"
        else:  # Drone is below requirement
            if fm_battery["long"][0] > fm_battery["medium"][0] and fm_battery["long"][0] > fm_battery["short"][0]:
                relevance = fm_battery["long"][0] * 0.5  # Example penalty factor
                drone_category_label = "long (but below user requirement)"
            elif fm_battery["medium"][0] > fm_battery["short"][0]:
                relevance = fm_battery["medium"][0] * 0.5  # Example penalty factor
                drone_category_label = "medium (but below user requirement)"
            else:
                relevance = fm_battery["short"][0] * 0.5  # Example penalty factor
                drone_category_label = "short (below user requirement)"

        total_detailed_score += weight * relevance
        total_weights_for_detailed_score += weight
        explanations.append(
            f"Battery: User wants >= {battery_val_user}min, Drone has {battery_val_drone}min (Drone category: '{drone_category_label}')")

    normalized_detailed_score = 0.0
    if total_weights_for_detailed_score > 0:
        normalized_detailed_score = total_detailed_score / total_weights_for_detailed_score

    return normalized_detailed_score, explanations


# --- Main Drone Selection Function ---
def get_top_drones(user_input_gui, weights_gui, k=8, W_knn=0.6, W_detailed=0.4):
    df = pd.read_csv("drones_dataset.csv")

    for col in df.select_dtypes(include=np.number).columns:  # Round numeric columns
        df[col] = df[col].round(2)

    user_input_df_temp = pd.DataFrame([user_input_gui])
    user_input_processed = preprocess_data(user_input_df_temp).iloc[0].to_dict()

    df_processed = preprocess_data(df)
    df_scaled, user_scaled_knn_vector, knn_feature_names, scaler = scale_features(df_processed, user_input_processed)

    knn_weights_array = prepare_knn_weights(knn_feature_names, user_input_gui.keys(), weights_gui)
    sqrt_knn_weights = np.sqrt(knn_weights_array)

    df_weighted_scaled_features = df_scaled[knn_feature_names].multiply(sqrt_knn_weights,
                                                                        axis=1)  # Correct way to multiply
    user_weighted_scaled_vector = user_scaled_knn_vector * sqrt_knn_weights

    # Ensure no NaN values are passed to NearestNeighbors
    df_weighted_scaled_features = df_weighted_scaled_features.fillna(0)
    user_weighted_scaled_vector = np.nan_to_num(user_weighted_scaled_vector)

    model = NearestNeighbors(n_neighbors=k, metric="euclidean")
    model.fit(df_weighted_scaled_features.values)  # Pass .values to avoid feature name warnings if df has names

    distances, indices = model.kneighbors(user_weighted_scaled_vector.reshape(1, -1))

    max_possible_weighted_scaled_vector = np.ones(len(knn_feature_names)) * sqrt_knn_weights
    max_dist = np.linalg.norm(max_possible_weighted_scaled_vector)
    if max_dist == 0: max_dist = 1.0  # Use float

    top_drones_data = []
    for dist, idx in zip(distances[0], indices[0]):
        drone_original_row = df.iloc[idx].copy()

        knn_similarity_score = max(0.0, 1.0 - (dist / max_dist)) if max_dist > 0 else 0.0

        detailed_score, fuzzy_explanations = compute_detailed_scores_and_explanations(
            drone_original_row, user_input_gui, weights_gui
        )

        total_score = (knn_similarity_score * W_knn + detailed_score * W_detailed) * 100.0

        general_explanations = []
        for feature_name, user_value in user_input_gui.items():
            if feature_name in ["Payload Capacity", "Budgets options", "Battery Life"]:
                continue
            drone_actual_value = drone_original_row.get(feature_name, "N/A")
            weight = weights_gui.get(feature_name, 0.0)
            match_info = ""
            # Ensure drone_actual_value is not "N/A" before numeric comparison
            if drone_actual_value != "N/A" and pd.api.types.is_numeric_dtype(
                    type(user_value)) and pd.api.types.is_numeric_dtype(type(drone_actual_value)):
                if float(drone_actual_value) > float(user_value):
                    match_info = "(Drone exceeds requirement)"
                elif float(drone_actual_value) < float(user_value):
                    match_info = "(Drone below requirement)"
                else:
                    match_info = "(Exact match)"
            elif str(user_value) == str(drone_actual_value):
                match_info = "(Match)"
            else:
                match_info = "(Does not match)"
            general_explanations.append(
                f"{feature_name}: Requested '{user_value}', Drone '{drone_actual_value}' {match_info}."
            )

        all_explanations = fuzzy_explanations + general_explanations

        top_drones_data.append({
            "Drone ID": drone_original_row["Drone ID"],
            "Total Score (%)": round(total_score, 2),
            "Price": drone_original_row.get("Budgets options", "N/A"),
            "Explanation": all_explanations,
            "_knn_dist": dist,
            "_knn_score": round(knn_similarity_score, 3),
            "_detailed_score": round(detailed_score, 3),
        })

    top_drones_data.sort(key=lambda x: x["Total Score (%)"], reverse=True)
    return top_drones_data[:3] # only top 3 drones



if __name__ == "__main__":
    user_input = {
        "Flight Radius": 7.0,
        "Flight height": 300.0,
        "Thermal/Night Camera": 1,
        "Max wind resistance": 10.0,
        "Budgets options": 8000.0,
        "Camera Quality": "4K",
        "ISO range": 3200,
        "Battery Life": 90.0,
        "Payload Capacity": 10.0,
        "Dimensions": 3000.0,
        "Real-time data transmission": 1,
        "Transmission bandwidth": 50.0,
        "Data storage ability": 128,
        "Air/Water quality sensor availability": 0,
        "Noise level": 50.0,
        "Operating Temperature": 20.0,
        "Class Identification Label": "C2",
        "Charging Time": 60.0,
        "Automatic Landing/Takeoff": 1,
        "GPS Supported Systems": "GPS+Galileo",
        "Automated Path Finding": 1
    }

    weights = {
        "Flight Radius": 1.5, "Flight height": 0.8, "Thermal/Night Camera": 2.0,
        "Max wind resistance": 1.2, "Budgets options": 15.0, "Camera Quality": 1.8,
        "ISO range": 0.7, "Battery Life": 2.5, "Payload Capacity": 1.5,
        "Dimensions": 0.5, "Real-time data transmission": 1.5,
        "Transmission bandwidth": 0.9, "Data storage ability": 1.0,
        "Air/Water quality sensor availability": 1.2, "Noise level": 0.6,
        "Operating Temperature": 1.5, "Class Identification Label": 1.0,
        "Charging Time": 0.5, "Automatic Landing/Takeoff": 0.5,
        "GPS Supported Systems": 0.5, "Automated Path Finding": 0.6
    }

    result = get_top_drones(user_input, weights, k=3, W_knn=0.6, W_detailed=0.4)

    print(f"\n--- TOP {len(result)} DRONES FOUND ---")
    for i, drone_info in enumerate(result):  # Renamed drone to drone_info to avoid conflict
        print(f"\n{i + 1}. Drone ID: {drone_info['Drone ID']}")
        print(
            f"   Total Score: {drone_info['Total Score (%)']}% (KNN: {drone_info['_knn_score']:.2f}, Detailed: {drone_info['_detailed_score']:.2f})")
        print(f"   Price: {drone_info['Price']}")
        print("   Detailed Explanations:")
        if drone_info["Explanation"]:
            for expl in drone_info["Explanation"]:
                print(f"   - {expl}")
        else:
            print("   - No explanations available.")