import json
import os

RULES_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'rules_config.json')

def load_rules():
    with open(RULES_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def detect_vision_type(add, age):
    if add and add > 0:
        if add <= 1.00:
            return "Presbyopia Awal", "Progressive disyorkan"
        elif add <= 2.00:
            return "Presbyopia Sederhana", "Progressive / Bifocal"
        else:
            return "Presbyopia Lanjut", "Progressive / Bifocal wajib"
    elif age and age >= 40:
        return "Single Vision (semak ADD)", "Mungkin memerlukan ADD — sila semak semula"
    else:
        return "Single Vision", "Spek jauh atau dekat sahaja"

def analyze_prescription(sph_r, cyl_r, sph_l, cyl_l, add, age, lifestyle=None):
    recommendations = []
    warnings = []
    refer = False
    rules = load_rules()

    # High power check
    for label, sph, cyl in [("Kanan", sph_r, cyl_r), ("Kiri", sph_l, cyl_l)]:
        se = sph + (cyl / 2)
        if abs(se) >= rules["high_index_threshold"]:
            recommendations.append(f"🔹 Mata {label}: Power tinggi (SE {se:.2f}D) — High Index Lens 1.67 atau 1.74 disyorkan")

    # Astigmatism check
    for label, cyl in [("Kanan", cyl_r), ("Kiri", cyl_l)]:
        if abs(cyl) >= rules["toric_threshold"]:
            recommendations.append(f"🔹 Mata {label}: Astigmatism tinggi ({cyl:.2f}D) — Toric lens untuk contact lens")

    # ADD / Presbyopia
    if add and add > 0:
        vision_type, lens_rec = detect_vision_type(add, age)
        recommendations.append(f"🔹 {vision_type} (ADD +{add:.2f}) — {lens_rec}")

    # Lifestyle recommendations
    if lifestyle:
        if "komputer" in lifestyle.lower() or "ofis" in lifestyle.lower():
            recommendations.append("🔹 Guna komputer — Blue Light Filter coating disyorkan")
        if "luar" in lifestyle.lower() or "outdoor" in lifestyle.lower():
            recommendations.append("🔹 Aktiviti luar — Photochromic atau UV coating disyorkan")
        if "memandu" in lifestyle.lower() or "drive" in lifestyle.lower():
            recommendations.append("🔹 Memandu — Anti-glare coating disyorkan")

    # Default coating
    if not recommendations or not any("coating" in r for r in recommendations):
        recommendations.append("🔹 Anti-glare coating standard disyorkan")

    # BVD warning
    for label, sph, cyl in [("Kanan", sph_r, cyl_r), ("Kiri", sph_l, cyl_l)]:
        if abs(sph) >= 4.0 or abs(sph + cyl) >= 4.0:
            warnings.append(f"⚠️ Mata {label}: Power ≥ ±4.00D — BVD compensation diperlukan")

    # Referral flags
    refer_symptoms = rules.get("refer_symptoms", [])
    if lifestyle:
        for symptom in refer_symptoms:
            if symptom.lower() in lifestyle.lower():
                warnings.append(f"🚨 Simptom '{symptom}' dikesan — Sila refer ke pakar mata (Ophthalmologist)")
                refer = True

    return recommendations, warnings, refer
