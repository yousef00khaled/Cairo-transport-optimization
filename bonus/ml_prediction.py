"""
ML-Based Traffic Prediction (Bonus).
Uses scikit-learn Random Forest to forecast congestion
based on temporal traffic data.
"""
import numpy as np
from data.cairo_data import TRAFFIC_FLOW, EXISTING_ROADS, TIME_PERIODS

# Try importing sklearn, gracefully handle if not installed
try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_absolute_error, r2_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class TrafficPredictor:
    """ML-based traffic flow predictor using Random Forest."""

    def __init__(self):
        self.model = None
        self.road_encoder = {}
        self.metrics = {}
        self.is_trained = False

    def _build_dataset(self):
        """
        Build training dataset from provided temporal traffic data.
        Expands data with synthetic variations (different days, slight noise).
        """
        X = []
        y = []

        # Encode road IDs
        roads = list(TRAFFIC_FLOW.keys())
        self.road_encoder = {road: i for i, road in enumerate(roads)}

        # For each road and time period, create training samples
        for road_key, flows in TRAFFIC_FLOW.items():
            road_id = self.road_encoder[road_key]

            for time_idx, flow in enumerate(flows):
                # Create variations for 7 days with noise
                for day in range(7):
                    # Day of week factor (weekday vs weekend)
                    is_weekend = 1 if day >= 5 else 0
                    day_factor = 0.7 if is_weekend else 1.0

                    # Add some random noise for realistic variation
                    noise = np.random.normal(0, flow * 0.05)  # 5% noise

                    features = [
                        road_id,           # Road identifier
                        time_idx,          # Time period (0-3)
                        day,               # Day of week (0-6)
                        is_weekend,        # Weekend flag
                        flow * day_factor, # Historical baseline
                    ]

                    target = flow * day_factor + noise

                    X.append(features)
                    y.append(max(0, target))  # Ensure non-negative

        return np.array(X), np.array(y)

    def train(self):
        """
        Train the Random Forest model on traffic data.

        Returns:
            dict with training metrics
        """
        if not SKLEARN_AVAILABLE:
            return {
                "error": "scikit-learn not installed. Run: pip install scikit-learn",
                "is_trained": False,
            }

        X, y = self._build_dataset()

        # Split into train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Train Random Forest
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1,
        )
        self.model.fit(X_train, y_train)

        # Evaluate
        y_pred = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        self.metrics = {
            "mae": round(mae, 2),
            "r2_score": round(r2, 4),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "features": ["road_id", "time_period", "day_of_week", "is_weekend", "historical_baseline"],
            "feature_importance": dict(zip(
                ["road_id", "time_period", "day_of_week", "is_weekend", "historical_baseline"],
                [round(fi, 4) for fi in self.model.feature_importances_]
            )),
        }
        self.is_trained = True

        return {
            "status": "trained",
            "is_trained": True,
            "metrics": self.metrics,
        }

    def predict(self, road_key, time_period="morning", day_of_week=0):
        """
        Predict traffic flow for a specific road and time.

        Args:
            road_key: Road identifier (e.g., "1-3")
            time_period: "morning", "afternoon", "evening", "night"
            day_of_week: 0=Monday ... 6=Sunday

        Returns:
            dict with predicted_flow, congestion_probability
        """
        if not self.is_trained:
            return {"error": "Model not trained. Call train() first."}

        road_id = self.road_encoder.get(road_key)
        if road_id is None:
            return {"error": f"Unknown road: {road_key}"}

        time_idx = TIME_PERIODS.index(time_period) if time_period in TIME_PERIODS else 0
        is_weekend = 1 if day_of_week >= 5 else 0

        # Get historical baseline
        baseline = TRAFFIC_FLOW.get(road_key, (1000, 1000, 1000, 1000))[time_idx]

        features = np.array([[road_id, time_idx, day_of_week, is_weekend, baseline]])
        predicted_flow = max(0, self.model.predict(features)[0])

        # Get capacity for congestion probability
        capacity = 3000  # Default
        for frm, to, dist, cap, cond in EXISTING_ROADS:
            if f"{frm}-{to}" == road_key or f"{to}-{frm}" == road_key:
                capacity = cap
                break

        congestion_ratio = predicted_flow / capacity
        congestion_prob = min(1.0, max(0.0, (congestion_ratio - 0.5) / 0.5))

        return {
            "road": road_key,
            "time_period": time_period,
            "day_of_week": day_of_week,
            "day_name": ["Monday", "Tuesday", "Wednesday", "Thursday",
                         "Friday", "Saturday", "Sunday"][day_of_week],
            "predicted_flow": int(predicted_flow),
            "capacity": capacity,
            "congestion_ratio": round(congestion_ratio, 2),
            "congestion_probability": round(congestion_prob, 2),
            "congestion_level": (
                "Low" if congestion_prob < 0.3 else
                "Moderate" if congestion_prob < 0.6 else
                "High" if congestion_prob < 0.8 else
                "Severe"
            ),
        }

    def predict_all_roads(self, time_period="morning", day_of_week=0):
        """Predict traffic for all roads."""
        if not self.is_trained:
            return {"error": "Model not trained."}

        predictions = []
        for road_key in TRAFFIC_FLOW:
            pred = self.predict(road_key, time_period, day_of_week)
            if "error" not in pred:
                predictions.append(pred)

        predictions.sort(key=lambda x: x["congestion_ratio"], reverse=True)

        return {
            "time_period": time_period,
            "day_of_week": day_of_week,
            "predictions": predictions,
            "high_congestion_count": sum(1 for p in predictions if p["congestion_level"] in ["High", "Severe"]),
            "model_metrics": self.metrics,
        }


# Singleton instance
_predictor = TrafficPredictor()


def get_predictor():
    """Get the singleton predictor instance."""
    return _predictor
