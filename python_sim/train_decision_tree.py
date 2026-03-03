#!/usr/bin/env python3
"""
train_decision_tree.py  –  Generate training data + export Decision Tree to C
==============================================================================

This script:
  1. Generates a synthetic dataset of (9-sensor-input → action) pairs
     using the expert rule-based policy as ground truth.
  2. Trains a compact Decision Tree classifier (max_depth=6).
  3. Exports the tree as pure-C if/else code for the ESP32.

The exported model replaces the hard-coded placeholder weights in the
ESP32 firmware with a *real trained model*.

Classes (actions):
    0 = GO_STRAIGHT   – no significant obstacle
    1 = VEER_LEFT     – obstacle on right, steer left
    2 = VEER_RIGHT    – obstacle on left, steer right
    3 = HARD_LEFT     – close obstacle right / front-right
    4 = HARD_RIGHT    – close obstacle left / front-left
    5 = EMERGENCY_STOP – very close front obstacle, reverse+spin

Speed output is encoded as a second DT regressor (max_depth=4).

Run:  python train_decision_tree.py
"""

import random, math, json, os
import numpy as np

# ─── Expert policy (mirrors ESP32 rule-based logic) ─────────────
DMAX = 5.5

def expert_policy(sensors: list) -> tuple:
    """
    Given 9 sensor readings [LS, LF, LM, LN, C, RN, RM, RF, RS]
    return (action_class, speed_scale).

    Thresholds are deliberately CONSERVATIVE so the robot starts
    reacting well before it can physically collide (robot_radius=0.18 m,
    sensor_offset=0.10 m ⇒ collision @ sensor ≈ 0.08 m).
    """
    dLS, dLF, dLM, dLN, dC, dRN, dRM, dRF, dRS = sensors

    front = dC
    left_min = min(dLS, dLF, dLM, dLN)
    right_min = min(dRN, dRM, dRF, dRS)
    min_all = min(front, left_min, right_min)

    # ── Emergency: way too close → full stop + hard turn ──────
    if front < 0.45 or min_all < 0.35:
        speed = 0.0
        if left_min > right_min:
            return (3, speed)   # HARD_LEFT
        else:
            return (4, speed)   # HARD_RIGHT

    # ── Critical: must turn sharply NOW ───────────────────────
    if front < 0.70:
        speed = 0.05
        if left_min > right_min:
            return (3, speed)
        else:
            return (4, speed)

    # ── Danger: moderate correction ───────────────────────────
    if front < 1.10:
        speed = 0.18
        if left_min > right_min:
            return (1, speed)   # VEER_LEFT
        else:
            return (2, speed)   # VEER_RIGHT

    # ── Side warning: obstacle beside us ──────────────────────
    if left_min < 0.70:
        return (2, 0.30)        # VEER_RIGHT away from left wall
    if right_min < 0.70:
        return (1, 0.30)        # VEER_LEFT away from right wall

    # ── Caution: obstacle visible ahead ───────────────────────
    if front < 1.60:
        speed = 0.40
        asym = left_min - right_min
        if asym < -0.15:
            return (1, speed)
        elif asym > 0.15:
            return (2, speed)
        else:
            return (0, speed)   # GO_STRAIGHT

    # ── Safe: cruise ──────────────────────────────────────────
    return (0, min(1.0, 0.5 + 0.5 * (min_all / DMAX)))


# ─── Dataset generation ─────────────────────────────────────────
def generate_dataset(n: int = 20000, seed: int = 42) -> tuple:
    rng = random.Random(seed)
    X, y_cls, y_spd = [], [], []

    for _ in range(n):
        sensors = []
        # Mix of close, mid, far readings to cover all scenarios
        scenario = rng.choice(["random", "close_front", "close_left",
                                "close_right", "corridor", "open"])
        for i in range(9):
            if scenario == "close_front" and 3 <= i <= 5:
                sensors.append(rng.uniform(0.1, 0.6))
            elif scenario == "close_left" and i <= 3:
                sensors.append(rng.uniform(0.1, 0.8))
            elif scenario == "close_right" and i >= 5:
                sensors.append(rng.uniform(0.1, 0.8))
            elif scenario == "corridor":
                if i <= 1 or i >= 7:
                    sensors.append(rng.uniform(0.2, 0.6))
                else:
                    sensors.append(rng.uniform(1.0, 3.0))
            elif scenario == "open":
                sensors.append(rng.uniform(2.0, DMAX))
            else:
                sensors.append(rng.uniform(0.1, DMAX))

        cls, spd = expert_policy(sensors)
        X.append(sensors)
        y_cls.append(cls)
        y_spd.append(spd)

    return np.array(X), np.array(y_cls), np.array(y_spd)


# ─── Decision-tree to C export ──────────────────────────────────
def tree_to_c(tree, feature_names, fn_name="dt_predict_action"):
    """Convert sklearn DecisionTreeClassifier to C if/else code."""
    from sklearn.tree import _tree

    tree_ = tree.tree_
    feat = tree_.feature
    thresh = tree_.threshold
    classes = tree.classes_

    lines = []
    lines.append(f"// Auto-generated Decision Tree  (depth={tree.get_depth()}, "
                 f"leaves={tree.get_n_leaves()}, classes={len(classes)})")
    lines.append(f"// Features: {feature_names}")
    lines.append(f"static int {fn_name}(const float f[9]) {{")

    def recurse(node, indent):
        pad = "    " * indent
        if feat[node] != _tree.TREE_UNDEFINED:
            f_idx = feat[node]
            thr = thresh[node]
            lines.append(f"{pad}if (f[{f_idx}] <= {thr:.4f}f) {{")
            recurse(tree_.children_left[node], indent + 1)
            lines.append(f"{pad}}} else {{")
            recurse(tree_.children_right[node], indent + 1)
            lines.append(f"{pad}}}")
        else:
            # Leaf
            value = tree_.value[node][0]
            cls_idx = int(np.argmax(value))
            cls_val = int(classes[cls_idx])
            lines.append(f"{pad}return {cls_val};")

    recurse(0, 1)
    lines.append("}")
    return "\n".join(lines)


def regressor_to_c(tree, feature_names, fn_name="dt_predict_speed"):
    """Convert sklearn DecisionTreeRegressor to C."""
    from sklearn.tree import _tree

    tree_ = tree.tree_
    feat = tree_.feature
    thresh = tree_.threshold

    lines = []
    lines.append(f"// Auto-generated Decision Tree Regressor  (depth={tree.get_depth()}, "
                 f"leaves={tree.get_n_leaves()})")
    lines.append(f"static float {fn_name}(const float f[9]) {{")

    def recurse(node, indent):
        pad = "    " * indent
        if feat[node] != _tree.TREE_UNDEFINED:
            f_idx = feat[node]
            thr = thresh[node]
            lines.append(f"{pad}if (f[{f_idx}] <= {thr:.4f}f) {{")
            recurse(tree_.children_left[node], indent + 1)
            lines.append(f"{pad}}} else {{")
            recurse(tree_.children_right[node], indent + 1)
            lines.append(f"{pad}}}")
        else:
            val = float(tree_.value[node][0][0])
            lines.append(f"{pad}return {val:.4f}f;")

    recurse(0, 1)
    lines.append("}")
    return "\n".join(lines)


# ─── Main ────────────────────────────────────────────────────────
def main():
    from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, mean_absolute_error

    print("=" * 60)
    print("  Decision Tree Training for ESP32 Embedded AI")
    print("=" * 60)

    # 1. Generate data
    print("\n[1/4] Generating synthetic dataset …")
    X, y_cls, y_spd = generate_dataset(n=40000)
    X_train, X_test, yc_train, yc_test, ys_train, ys_test = \
        train_test_split(X, y_cls, y_spd, test_size=0.2, random_state=42)
    print(f"  Train: {len(X_train)}, Test: {len(X_test)}")

    # 2. Train classifier
    print("\n[2/4] Training action classifier (max_depth=8) …")
    clf = DecisionTreeClassifier(max_depth=8, random_state=42)
    clf.fit(X_train, yc_train)
    acc = clf.score(X_test, yc_test)
    print(f"  Accuracy: {acc:.4f}")
    print(classification_report(yc_test, clf.predict(X_test),
          target_names=["GO_STRAIGHT","VEER_LEFT","VEER_RIGHT",
                        "HARD_LEFT","HARD_RIGHT"]))

    # 3. Train speed regressor
    print("[3/4] Training speed regressor (max_depth=6) …")
    reg = DecisionTreeRegressor(max_depth=6, random_state=42)
    reg.fit(X_train, ys_train)
    mae = mean_absolute_error(ys_test, reg.predict(X_test))
    print(f"  MAE: {mae:.4f}")

    # 4. Export to C header
    print("\n[4/4] Exporting to C header …")
    feature_names = ["dLS","dLF","dLM","dLN","dC","dRN","dRM","dRF","dRS"]
    c_clf = tree_to_c(clf, feature_names, "dt_predict_action")
    c_reg = regressor_to_c(reg, feature_names, "dt_predict_speed")

    header = f"""#ifndef DECISION_TREE_MODEL_H
#define DECISION_TREE_MODEL_H
/*
 * decision_tree_model.h
 * =====================
 * Auto-generated Decision Tree model for ESP32 Embedded AI.
 *
 * Action classes:
 *   0 = GO_STRAIGHT   – path clear, drive forward
 *   1 = VEER_LEFT     – moderate left correction
 *   2 = VEER_RIGHT    – moderate right correction
 *   3 = HARD_LEFT     – sharp left / spin
 *   4 = HARD_RIGHT    – sharp right / spin
 *
 * Input: float f[9] – normalised sensor distances
 *   Index order: [LS, LF, LM, LN, C, RN, RM, RF, RS]
 *
 * Generated from {len(X_train)} training samples.
 * Classifier accuracy: {acc:.4f}
 * Speed regressor MAE: {mae:.4f}
 */

/* Action labels */
#define DT_GO_STRAIGHT  0
#define DT_VEER_LEFT    1
#define DT_VEER_RIGHT   2
#define DT_HARD_LEFT    3
#define DT_HARD_RIGHT   4

{c_clf}

{c_reg}

#endif /* DECISION_TREE_MODEL_H */
"""

    # Write to esp32 firmware directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(script_dir, "..", "esp32_wokwi", "sketch_improved")
    out_path = os.path.join(out_dir, "decision_tree_model.h")
    os.makedirs(out_dir, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(header)
    print(f"  ✓ Written → {out_path}")

    # Also write a compact stats JSON for documentation
    stats = {
        "classifier_depth": int(clf.get_depth()),
        "classifier_leaves": int(clf.get_n_leaves()),
        "classifier_accuracy": round(float(acc), 4),
        "regressor_depth": int(reg.get_depth()),
        "regressor_leaves": int(reg.get_n_leaves()),
        "regressor_mae": round(float(mae), 4),
        "training_samples": len(X_train),
        "test_samples": len(X_test),
        "features": feature_names,
    }
    stats_path = os.path.join(out_dir, "model_stats.json")
    with open(stats_path, "w") as f:
        json.dump(stats, f, indent=2)
    print(f"  ✓ Stats  → {stats_path}")
    print("\n✅ Done!")


if __name__ == "__main__":
    main()
