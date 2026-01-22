import json

# Concepts and Terms
concepts = {
    "md_diet": {
        "mesh": ["Diet, Mediterranean", "Diet, Healthy"],
        "emtree": ["Mediterranean diet", "healthy diet"],
        "tiab": ["Mediterranean diet", "med diet", "mediterranean style diet", "mediterranean food", "mediterranean cuisine", "cretan diet"]
    },
    "components": {
        "mesh": ["Fruit", "Vegetables", "Edible Grain", "Fabaceae", "Dairy Products", "Seafood", "Meat", "Olive Oil", "Wine", "Alcohol Drinking"],
        "emtree": ["fruit", "vegetable", "cereal", "legume", "dairy product", "seafood", "meat", "olive oil", "wine", "alcohol consumption"],
        "tiab": ["fruit*", "vegetable*", "cereal*", "grain*", "legume*", "bean*", "nut*", "dairy", "milk", "cheese", "yogurt", "yoghurt", "fish", "seafood", "meat", "poultry", "olive oil", "wine", "alcohol"]
    },
    "sleep": {
        "mesh": ["Sleep", "Sleep Wake Disorders", "Sleep Apnea Syndromes", "Dyssomnias", "Circadian Rhythm"],
        "emtree": ["sleep", "sleep disorder", "sleep apnea syndrome", "dyssomnia", "circadian rhythm"],
        "tiab": ["sleep*", "insomnia*", "dyssomnia*", "parasomnia*", "apnea", "hypopnea", "wakeful*", "drowsy", "drowsiness", "somnolence", "tiredness", "napping", "circadian"]
    }
}

# Helper to join with OR
def join_or(terms):
    return " OR ".join(terms)

# Helper to join with AND
def join_and(terms):
    return " AND ".join(terms)

# --- PubMed Generation ---
def generate_pubmed(variant):
    # Base Terms
    md_mesh = [f"{t}[Mesh]" for t in concepts["md_diet"]["mesh"]]
    comp_mesh = [f"{t}[Mesh]" for t in concepts["components"]["mesh"]]
    sl_mesh = [f"{t}[Mesh]" for t in concepts["sleep"]["mesh"]]
    
    md_tiab = [f"{t}[tiab]" for t in concepts["md_diet"]["tiab"]]
    comp_tiab = [f"{t}[tiab]" for t in concepts["components"]["tiab"]]
    sl_tiab = [f"{t}[tiab]" for t in concepts["sleep"]["tiab"]]

    # Recall: All Mesh + All TiAb
    if variant == "recall":
        p1 = join_or(md_mesh + md_tiab + comp_mesh + comp_tiab)
        p2 = join_or(sl_mesh + sl_tiab)
        return f"({p1}) AND ({p2})"

    # Balanced: Mesh + TiAb
    if variant == "balanced":
        p1 = join_or(md_mesh + md_tiab + comp_mesh + comp_tiab)
        p2 = join_or(sl_mesh + sl_tiab)
        return f"({p1}) AND ({p2})"

    # Precision: Major Mesh + Title Only (Simulated Precision for now)
    if variant == "precision":
        md_majr = [f"{t}[majr]" for t in concepts["md_diet"]["mesh"]]
        sl_majr = [f"{t}[majr]" for t in concepts["sleep"]["mesh"]]
        md_ti = [f"{t}[ti]" for t in concepts["md_diet"]["tiab"]]
        sl_ti = [f"{t}[ti]" for t in concepts["sleep"]["tiab"]]
        p1 = join_or(md_majr + md_ti) # Note: Components might be dropped in strict precision or kept as Majr
        # To match "High-precision: (Emphasize major focus terms and specific synonyms)" we keep components but strict
        comp_majr = [f"{t}[majr]" for t in concepts["components"]["mesh"]]
        comp_ti = [f"{t}[ti]" for t in concepts["components"]["tiab"]]
        p1 = join_or(md_majr + md_ti + comp_majr + comp_ti)
        p2 = join_or(sl_majr + sl_ti)
        return f"({p1}) AND ({p2})"
    
    # Micro 1: Filter (Humans)
    if variant == "micro1":
        base = generate_pubmed("balanced")
        return f"{base} AND humans[Filter]"

    # Micro 2: Scope (Title)
    if variant == "micro2":
         # Re-implement balanced but restricted to [ti]
        md_ti = [f"{t}[ti]" for t in concepts["md_diet"]["tiab"]]
        comp_ti = [f"{t}[ti]" for t in concepts["components"]["tiab"]]
        sl_ti = [f"{t}[ti]" for t in concepts["sleep"]["tiab"]]
        # Keep Mesh? Usually Scope-based means narrowing field. Let's keep Mesh but restrict text to TI.
        md_mesh = [f"{t}[Mesh]" for t in concepts["md_diet"]["mesh"]]
        comp_mesh = [f"{t}[Mesh]" for t in concepts["components"]["mesh"]]
        sl_mesh = [f"{t}[Mesh]" for t in concepts["sleep"]["mesh"]]
        
        p1 = join_or(md_mesh + md_ti + comp_mesh + comp_ti)
        p2 = join_or(sl_mesh + sl_ti)
        return f"({p1}) AND ({p2})"

    # Micro 3: Proximity -> Fallback to Majr in PubMed
    if variant == "micro3":
        # Fallback to Majr as per instructions
        md_majr = [f"{t}[majr]" for t in concepts["md_diet"]["mesh"]]
        comp_majr = [f"{t}[majr]" for t in concepts["components"]["mesh"]]
        sl_majr = [f"{t}[majr]" for t in concepts["sleep"]["mesh"]]
        # And maybe Tiab for text
        md_tiab = [f"{t}[tiab]" for t in concepts["md_diet"]["tiab"]]
        comp_tiab = [f"{t}[tiab]" for t in concepts["components"]["tiab"]]
        sl_tiab = [f"{t}[tiab]" for t in concepts["sleep"]["tiab"]]
        
        p1 = join_or(md_majr + md_tiab + comp_majr + comp_tiab)
        p2 = join_or(sl_majr + sl_tiab)
        return f"({p1}) AND ({p2})"

# --- Scopus Generation ---
def generate_scopus(variant):
    # Terms
    md_terms = concepts["md_diet"]["tiab"]
    comp_terms = concepts["components"]["tiab"]
    sl_terms = concepts["sleep"]["tiab"]
    
    def wrap(t): return f'"{t}"' if " " in t else t
    
    md_str = " OR ".join([wrap(t) for t in md_terms])
    comp_str = " OR ".join([wrap(t) for t in comp_terms])
    sl_str = " OR ".join([wrap(t) for t in sl_terms])
    
    combined_md = f"({md_str} OR {comp_str})"
    combined_sl = f"({sl_str})"

    if variant == "recall":
        return f"TITLE-ABS-KEY({combined_md} AND {combined_sl})"
    
    if variant == "balanced":
        return f"TITLE-ABS-KEY({combined_md} AND {combined_sl})"

    if variant == "precision":
        return f"TITLE({combined_md} AND {combined_sl})"

    if variant == "micro1": # Filter
        return f"TITLE-ABS-KEY({combined_md} AND {combined_sl}) AND DOCTYPE(ar OR re)"

    if variant == "micro2": # Scope
        return f"TITLE({combined_md} AND {combined_sl})"

    if variant == "micro3": # Proximity W/5
        # Scopus Proximity: (A W/5 B)
        # Note: (OR) W/5 (OR) is valid in Scopus
        return f"TITLE-ABS-KEY({combined_md} W/5 {combined_sl})"

# --- WoS Generation ---
def generate_wos(variant):
    md_terms = concepts["md_diet"]["tiab"]
    comp_terms = concepts["components"]["tiab"]
    sl_terms = concepts["sleep"]["tiab"]

    def wrap(t): return f'"{t}"' if " " in t else t

    md_str = " OR ".join([wrap(t) for t in md_terms])
    comp_str = " OR ".join([wrap(t) for t in comp_terms])
    sl_str = " OR ".join([wrap(t) for t in sl_terms])

    combined_md = f"({md_str} OR {comp_str})"
    combined_sl = f"({sl_str})"

    if variant == "recall":
        return f"TS=({combined_md} AND {combined_sl})"
    
    if variant == "balanced":
        return f"TS=({combined_md} AND {combined_sl})"

    if variant == "precision":
        return f"TI=({combined_md} AND {combined_sl})"

    if variant == "micro1": # Filter
        return f"TS=({combined_md} AND {combined_sl}) AND DT=(Article OR Review)"

    if variant == "micro2": # Scope
        return f"TI=({combined_md} AND {combined_sl})"

    if variant == "micro3": # Proximity NEAR/5
        return f"TS=({combined_md} NEAR/5 {combined_sl})"

# --- Embase Generation ---
def generate_embase(variant):
    # Emtree
    md_tree = [f