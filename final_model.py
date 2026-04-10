from prep_data import X_train_scaled, X_test_scaled, y_train, y_test

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, recall_score, roc_auc_score

# -----------------------------
# 1. TRAIN FINAL MODEL
# -----------------------------
model = LogisticRegression(max_iter=5000, class_weight="balanced")
model.fit(X_train_scaled, y_train)

# -----------------------------
# 2. PREDICTIONS
# -----------------------------
y_pred = model.predict(X_test_scaled)
y_prob = model.predict_proba(X_test_scaled)[:, 1]

# -----------------------------
# 3. FINAL MODEL PERFORMANCE
# -----------------------------
print("\nFINAL MODEL PERFORMANCE")
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Recall:", recall_score(y_test, y_pred))
print("AUC:", roc_auc_score(y_test, y_prob))

# -----------------------------
# 4. RISK CATEGORIES
# -----------------------------
def risk_category(prob):
    if prob < 0.2:
        return "Low Risk"
    elif prob < 0.5:
        return "Medium Risk"
    else:
        return "High Risk"

risk_labels = [risk_category(p) for p in y_prob]

print("\nSample Risk Predictions:")
for i in range(10):
    print(f"{y_prob[i]:.3f} -> {risk_labels[i]}")