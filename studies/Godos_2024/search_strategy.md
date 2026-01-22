# Search Strategy: Mediterranean Diet and Sleep

## 1. Concept Tables

### Concept 1: Mediterranean Diet & Components (Intervention)
| Concept | MeSH / Emtree | Tree Note | Explode? | Rationale & Source |
| :--- | :--- | :--- | :--- | :--- |
| **Med Diet** | `Diet, Mediterranean` (MeSH)<br>`Mediterranean diet` (Emtree) | | Yes | Core intervention. |
| **Fruit** | `Fruit` (MeSH)<br>`fruit` (Emtree) | | Yes | Protocol component. |
| **Vegetables** | `Vegetables` (MeSH)<br>`vegetable` (Emtree) | | Yes | Protocol component. |
| **Cereals** | `Edible Grain` (MeSH)<br>`cereal` (Emtree) | | Yes | Protocol component (Cereals/Grains). |
| **Legumes** | `Fabaceae` (MeSH)<br>`legume` (Emtree) | | Yes | Protocol component. |
| **Dairy** | `Dairy Products` (MeSH)<br>`dairy product` (Emtree) | | Yes | Protocol component. |
| **Fish/Seafood** | `Seafood` (MeSH), `Fishes` (MeSH)<br>`sea food` (Emtree) | | Yes | Protocol component. |
| **Meat** | `Meat` (MeSH)<br>`meat` (Emtree) | | Yes | Protocol component. |
| **Olive Oil** | `Olive Oil` (MeSH)<br>`olive oil` (Emtree) | | Yes | Protocol component. |
| **Alcohol** | `Alcohols` (MeSH), `Alcohol Drinking` (MeSH)<br>`alcohol` (Emtree) | | Yes | Protocol component. |

| Concept | Synonym/Phrase | Field | Truncation? | Source |
| :--- | :--- | :--- | :--- | :--- |
| **Med Diet** | "Mediterranean diet", "MedDiet" | tiab | No | Common abbreviations. |
| **Components** | fruit*, vegetable*, cereal*, grain*, legume*, bean*, dairy, milk, yogurt, cheese, fish, seafood, meat, poultry, "olive oil", alcohol*, wine | tiab | Yes | Protocol keywords and common food items. |

### Concept 2: Sleep (Outcome)
| Concept | MeSH / Emtree | Tree Note | Explode? | Rationale & Source |
| :--- | :--- | :--- | :--- | :--- |
| **Sleep** | `Sleep` (MeSH)<br>`sleep` (Emtree) | | Yes | Core outcome. |
| **Disorders** | `Sleep Wake Disorders` (MeSH)<br>`sleep disorder` (Emtree) | | Yes | Includes insomnia, apnea, etc. |

| Concept | Synonym/Phrase | Field | Truncation? | Source |
| :--- | :--- | :--- | :--- | :--- |
| **General** | sleep*, insomnia*, dyssomnia*, parasomnia*, hyposomnia*, hypersomnia* | tiab | Yes | Broad coverage of sleep states. |
| **Specific** | "short sleep", "long sleep", "sleep duration", "sleep quality", "daytime sleepiness", "somnolence" | tiab | No | Specific features mentioned in protocol. |

---

## 2. JSON Query Object

```json
{
  "pubmed": [
    "# High-recall: Broadest MeSH expansion and all text word variations",
    "((\"Diet, Mediterranean\"[Mesh] OR \"Mediterranean diet\"[tiab] OR \"MedDiet\"[tiab] OR \"Fruit\"[Mesh] OR fruit*[tiab] OR \"Vegetables\"[Mesh] OR vegetable*[tiab] OR \"Edible Grain\"[Mesh] OR cereal*[tiab] OR grain*[tiab] OR \"Fabaceae\"[Mesh] OR legume*[tiab] OR bean*[tiab] OR \"Dairy Products\"[Mesh] OR dairy[tiab] OR milk[tiab] OR yogurt[tiab] OR cheese[tiab] OR \"Seafood\"[Mesh] OR \"Fishes\"[Mesh] OR fish[tiab] OR seafood[tiab] OR \"Meat\"[Mesh] OR meat[tiab] OR poultry[tiab] OR \"Olive Oil\"[Mesh] OR \"olive oil\"[tiab] OR \"Alcohols\"[Mesh] OR \"Alcohol Drinking\"[Mesh] OR alcohol*[tiab] OR wine[tiab]) AND (\"Sleep\"[Mesh] OR \"Sleep Wake Disorders\"[Mesh] OR sleep*[tiab] OR insomnia*[tiab] OR dyssomnia*[tiab] OR parasomnia*[tiab] OR somnolence[tiab] OR \"sleep quality\"[tiab] OR \"sleep duration\"[tiab])) AND (\"1990/01/01\"[Date - Publication] : \"2023/12/31\"[Date - Publication])",
    "# Balanced: MeSH and text words, focused on Title/Abstract",
    "((\"Diet, Mediterranean\"[Mesh] OR \"Mediterranean diet\"[tiab] OR \"MedDiet\"[tiab] OR \"Fruit\"[Mesh] OR fruit*[tiab] OR \"Vegetables\"[Mesh] OR vegetable*[tiab] OR \"Edible Grain\"[Mesh] OR cereal*[tiab] OR grain*[tiab] OR \"Fabaceae\"[Mesh] OR legume*[tiab] OR bean*[tiab] OR \"Dairy Products\"[Mesh] OR dairy[tiab] OR milk[tiab] OR yogurt[tiab] OR cheese[tiab] OR \"Seafood\"[Mesh] OR \"Fishes\"[Mesh] OR fish[tiab] OR seafood[tiab] OR \"Meat\"[Mesh] OR meat[tiab] OR poultry[tiab] OR \"Olive Oil\"[Mesh] OR \"olive oil\"[tiab] OR \"Alcohols\"[Mesh] OR \"Alcohol Drinking\"[Mesh] OR alcohol*[tiab] OR wine[tiab]) AND (\"Sleep\"[Mesh] OR \"Sleep Wake Disorders\"[Mesh] OR sleep*[tiab] OR insomnia*[tiab] OR dyssomnia*[tiab] OR parasomnia*[tiab] OR somnolence[tiab] OR \"sleep quality\"[tiab] OR \"sleep duration\"[tiab])) AND (\"1990/01/01\"[Date - Publication] : \"2023/12/31\"[Date - Publication])",
    "# High-precision: Major MeSH topics and Title-only text words",
    "((\"Diet, Mediterranean\"[Majr] OR \"Mediterranean diet\"[ti] OR \"Fruit\"[Majr] OR fruit*[ti] OR \"Vegetables\"[Majr] OR vegetable*[ti] OR \"Edible Grain\"[Majr] OR cereal*[ti] OR grain*[ti] OR \"Fabaceae\"[Majr] OR legume*[ti] OR bean*[ti] OR \"Dairy Products\"[Majr] OR dairy[ti] OR \"Seafood\"[Majr] OR \"Meat\"[Majr] OR \"Olive Oil\"[Majr] OR \"Alcohols\"[Majr]) AND (\"Sleep\"[Majr] OR \"Sleep Wake Disorders\"[Majr] OR sleep*[ti] OR insomnia*[ti])) AND (\"1990/01/01\"[Date - Publication] : \"2023/12/31\"[Date - Publication])",
    "# Micro-variant 1 (Filter-based): Balanced query + Humans filter",
    "((\"Diet, Mediterranean\"[Mesh] OR \"Mediterranean diet\"[tiab] OR \"MedDiet\"[tiab] OR \"Fruit\"[Mesh] OR fruit*[tiab] OR \"Vegetables\"[Mesh] OR vegetable*[tiab] OR \"Edible Grain\"[Mesh] OR cereal*[tiab] OR grain*[tiab] OR \"Fabaceae\"[Mesh] OR legume*[tiab] OR bean*[tiab] OR \"Dairy Products\"[Mesh] OR dairy[tiab] OR milk[tiab] OR yogurt[tiab] OR cheese[tiab] OR \"Seafood\"[Mesh] OR \"Fishes\"[Mesh] OR fish[tiab] OR seafood[tiab] OR \"Meat\"[Mesh] OR meat[tiab] OR poultry[tiab] OR \"Olive Oil\"[Mesh] OR \"olive oil\"[tiab] OR \"Alcohols\"[Mesh] OR \"Alcohol Drinking\"[Mesh] OR alcohol*[tiab] OR wine[tiab]) AND (\"Sleep\"[Mesh] OR \"Sleep Wake Disorders\"[Mesh] OR sleep*[tiab] OR insomnia*[tiab] OR dyssomnia*[tiab] OR parasomnia*[tiab] OR somnolence[tiab] OR \"sleep quality\"[tiab] OR \"sleep duration\"[tiab])) AND (\"1990/01/01\"[Date - Publication] : \"2023/12/31\"[Date - Publication]) AND humans[Filter]",
    "# Micro-variant 2 (Field/Scope-based): Balanced query restricted to Title",
    "((\"Diet, Mediterranean\"[Mesh] OR \"Mediterranean diet\"[ti] OR \"MedDiet\"[ti] OR \"Fruit\"[Mesh] OR fruit*[ti] OR \"Vegetables\"[Mesh] OR vegetable*[ti] OR \"Edible Grain\"[Mesh] OR cereal*[ti] OR grain*[ti] OR \"Fabaceae\"[Mesh] OR legume*[ti] OR bean*[ti] OR \"Dairy Products\"[Mesh] OR dairy[ti] OR milk[ti] OR yogurt[ti] OR cheese[ti] OR \"Seafood\"[Mesh] OR fish[ti] OR \"Meat\"[Mesh] OR meat[ti] OR \"Olive Oil\"[Mesh] OR \"olive oil\"[ti] OR \"Alcohols\"[Mesh] OR alcohol*[ti]) AND (\"Sleep\"[Mesh] OR \"Sleep Wake Disorders\"[Mesh] OR sleep*[ti] OR insomnia*[ti])) AND (\"1990/01/01\"[Date - Publication] : \"2023/12/31\"[Date - Publication])",
    "# Micro-variant 3 (Proximity-based): PubMed fallback to Major MeSH focus (replaces proximity)",
    "((\"Diet, Mediterranean\"[Majr] OR \"Mediterranean diet\"[tiab] OR \"Fruit\"[Majr] OR \"Vegetables\"[Majr] OR \"Edible Grain\"[Majr] OR \"Fabaceae\"[Majr] OR \"Dairy Products\"[Majr] OR \"Seafood\"[Majr] OR \"Meat\"[Majr] OR \"Olive Oil\"[Majr] OR \"Alcohols\"[Majr]) AND (\"Sleep\"[Majr] OR \"Sleep Wake Disorders\"[Majr])) AND (\"1990/01/01\"[Date - Publication] : \"2023/12/31\"[Date - Publication])"
  ],
  "scopus": [
    "# High-recall: Broad TITLE-ABS-KEY search for all concepts",
    "(TITLE-ABS-KEY(\"Mediterranean diet\" OR \"MedDiet\" OR fruit* OR vegetable* OR cereal* OR grain* OR legume* OR bean* OR dairy OR milk OR yogurt OR cheese OR fish OR seafood OR meat OR poultry OR \"olive oil\" OR alcohol* OR wine) AND TITLE-ABS-KEY(sleep* OR insomnia* OR dyssomnia* OR parasomnia* OR somnolence OR \"sleep quality\" OR \"sleep duration\")) AND (PUBYEAR > 1989 AND PUBYEAR < 2024)",
    "# Balanced: Same as High-recall for Scopus (standard strategy)",
    "(TITLE-ABS-KEY(\"Mediterranean diet\" OR \"MedDiet\" OR fruit* OR vegetable* OR cereal* OR grain* OR legume* OR bean* OR dairy OR milk OR yogurt OR cheese OR fish OR seafood OR meat OR poultry OR \"olive oil\" OR alcohol* OR wine) AND TITLE-ABS-KEY(sleep* OR insomnia* OR dyssomnia* OR parasomnia* OR somnolence OR \"sleep quality\" OR \"sleep duration\")) AND (PUBYEAR > 1989 AND PUBYEAR < 2024)",
    "# High-precision: Title field restriction for all terms",
    "(TITLE(\"Mediterranean diet\" OR \"MedDiet\" OR fruit* OR vegetable* OR cereal* OR grain* OR legume* OR bean* OR dairy OR fish OR meat OR \"olive oil\" OR alcohol*) AND TITLE(sleep* OR insomnia* OR dyssomnia*)) AND (PUBYEAR > 1989 AND PUBYEAR < 2024)",
    "# Micro-variant 1 (Filter-based): Balanced query + Document Type (Article/Review)",
    "(TITLE-ABS-KEY(\"Mediterranean diet\" OR \"MedDiet\" OR fruit* OR vegetable* OR cereal* OR grain* OR legume* OR bean* OR dairy OR milk OR yogurt OR cheese OR fish OR seafood OR meat OR poultry OR \"olive oil\" OR alcohol* OR wine) AND TITLE-ABS-KEY(sleep* OR insomnia* OR dyssomnia* OR parasomnia* OR somnolence OR \"sleep quality\" OR \"sleep duration\")) AND (PUBYEAR > 1989 AND PUBYEAR < 2024) AND (DOCTYPE(ar OR re))",
    "# Micro-variant 2 (Field/Scope-based): Balanced query + Title restriction (Scope)",
    "(TITLE(\"Mediterranean diet\" OR \"MedDiet\" OR fruit* OR vegetable* OR cereal* OR grain* OR legume* OR bean* OR dairy OR fish OR meat OR \"olive oil\" OR alcohol*) AND TITLE(sleep* OR insomnia* OR dyssomnia*)) AND (PUBYEAR > 1989 AND PUBYEAR < 2024)",
    "# Micro-variant 3 (Proximity-based): Balanced query + Proximity operator (W/5)",
    "(TITLE-ABS-KEY(\"Mediterranean diet\" OR \"MedDiet\" OR fruit* OR vegetable* OR cereal* OR grain* OR legume* OR bean* OR dairy OR fish OR meat OR \"olive oil\" OR alcohol*) W/5 TITLE-ABS-KEY(sleep* OR insomnia* OR dyssomnia*)) AND (PUBYEAR > 1989 AND PUBYEAR < 2024)"
  ],
  "wos": [
    "# High-recall: Topic search (TS) for all concepts",
    "(TS=(\"Mediterranean diet\" OR \"MedDiet\" OR fruit* OR vegetable* OR cereal* OR grain* OR legume* OR bean* OR dairy OR milk OR yogurt OR cheese OR fish OR seafood OR meat OR poultry OR \"olive oil\" OR alcohol* OR wine) AND TS=(sleep* OR insomnia* OR dyssomnia* OR parasomnia* OR somnolence OR \"sleep quality\" OR \"sleep duration\")) AND PY=(1990-2023)",
    "# Balanced: Topic search (TS) for all concepts",
    "(TS=(\"Mediterranean diet\" OR \"MedDiet\" OR fruit* OR vegetable* OR cereal* OR grain* OR legume* OR bean* OR dairy OR milk OR yogurt OR cheese OR fish OR seafood OR meat OR poultry OR \"olive oil\" OR alcohol* OR wine) AND TS=(sleep* OR insomnia* OR dyssomnia* OR parasomnia* OR somnolence OR \"sleep quality\" OR \"sleep duration\")) AND PY=(1990-2023)",
    "# High-precision: Title search (TI)",
    "(TI=(\"Mediterranean diet\" OR \"MedDiet\" OR fruit* OR vegetable* OR cereal* OR grain* OR legume* OR bean* OR dairy OR fish OR meat OR \"olive oil\" OR alcohol*) AND TI=(sleep* OR insomnia* OR dyssomnia*)) AND PY=(1990-2023)",
    "# Micro-variant 1 (Filter-based): Balanced + Document Type (Article/Review)",
    "(TS=(\"Mediterranean diet\" OR \"MedDiet\" OR fruit* OR vegetable* OR cereal* OR grain* OR legume* OR bean* OR dairy OR milk OR yogurt OR cheese OR fish OR seafood OR meat OR poultry OR \"olive oil\" OR alcohol* OR wine) AND TS=(sleep* OR insomnia* OR dyssomnia* OR parasomnia* OR somnolence OR \"sleep quality\" OR \"sleep duration\")) AND PY=(1990-2023) AND DT=(Article OR Review)",
    "# Micro-variant 2 (Field/Scope-based): Balanced + Title restriction",
    "(TI=(\"Mediterranean diet\" OR \"MedDiet\" OR fruit* OR vegetable* OR cereal* OR grain* OR legume* OR bean* OR dairy OR fish OR meat OR \"olive oil\" OR alcohol*) AND TI=(sleep* OR insomnia* OR dyssomnia*)) AND PY=(1990-2023)",
    "# Micro-variant 3 (Proximity-based): Balanced + NEAR/5 operator",
    "(TS=(\"Mediterranean diet\" OR \"MedDiet\" OR fruit* OR vegetable* OR cereal* OR grain* OR legume* OR bean* OR dairy OR fish OR meat OR \"olive oil\" OR alcohol*) NEAR/5 TS=(sleep* OR insomnia* OR dyssomnia*)) AND PY=(1990-2023)"
  ],
  "embase": [
    "# High-recall: Emtree explosion and broad text words",
    "('Mediterranean diet'/exp OR 'Mediterranean diet':ti,ab OR 'MedDiet':ti,ab OR 'fruit'/exp OR 'fruit*':ti,ab OR 'vegetable'/exp OR 'vegetable*':ti,ab OR 'cereal'/exp OR 'cereal*':ti,ab OR 'grain*':ti,ab OR 'legume'/exp OR 'legume*':ti,ab OR 'bean*':ti,ab OR 'dairy product'/exp OR 'dairy':ti,ab OR 'milk':ti,ab OR 'yogurt':ti,ab OR 'cheese':ti,ab OR 'sea food'/exp OR 'fish':ti,ab OR 'seafood':ti,ab OR 'meat'/exp OR 'meat':ti,ab OR 'poultry':ti,ab OR 'olive oil'/exp OR 'olive oil':ti,ab OR 'alcohol'/exp OR 'alcohol*':ti,ab OR 'wine':ti,ab) AND ('sleep'/exp OR 'sleep disorder'/exp OR 'sleep*':ti,ab OR 'insomnia*':ti,ab OR 'dyssomnia*':ti,ab OR 'parasomnia*':ti,ab OR 'somnolence':ti,ab OR 'sleep quality':ti,ab OR 'sleep duration':ti,ab)",
    "# Balanced: Emtree explosion and text words",
    "('Mediterranean diet'/exp OR 'Mediterranean diet':ti,ab OR 'MedDiet':ti,ab OR 'fruit'/exp OR 'fruit*':ti,ab OR 'vegetable'/exp OR 'vegetable*':ti,ab OR 'cereal'/exp OR 'cereal*':ti,ab OR 'grain*':ti,ab OR 'legume'/exp OR 'legume*':ti,ab OR 'bean*':ti,ab OR 'dairy product'/exp OR 'dairy':ti,ab OR 'milk':ti,ab OR 'yogurt':ti,ab OR 'cheese':ti,ab OR 'sea food'/exp OR 'fish':ti,ab OR 'seafood':ti,ab OR 'meat'/exp OR 'meat':ti,ab OR 'poultry':ti,ab OR 'olive oil'/exp OR 'olive oil':ti,ab OR 'alcohol'/exp OR 'alcohol*':ti,ab OR 'wine':ti,ab) AND ('sleep'/exp OR 'sleep disorder'/exp OR 'sleep*':ti,ab OR 'insomnia*':ti,ab OR 'dyssomnia*':ti,ab OR 'parasomnia*':ti,ab OR 'somnolence':ti,ab OR 'sleep quality':ti,ab OR 'sleep duration':ti,ab)",
    "# High-precision: Focus terms (Major) and Title field",
    "(*'Mediterranean diet' OR *'fruit' OR *'vegetable' OR *'cereal' OR *'legume' OR *'dairy product' OR *'sea food' OR *'meat' OR *'olive oil' OR *'alcohol') AND (*'sleep' OR *'sleep disorder')",
    "# Micro-variant 1 (Filter-based): Balanced + Article/Review limit",
    "('Mediterranean diet'/exp OR 'Mediterranean diet':ti,ab OR 'MedDiet':ti,ab OR 'fruit'/exp OR 'fruit*':ti,ab OR 'vegetable'/exp OR 'vegetable*':ti,ab OR 'cereal'/exp OR 'cereal*':ti,ab OR 'grain*':ti,ab OR 'legume'/exp OR 'legume*':ti,ab OR 'bean*':ti,ab OR 'dairy product'/exp OR 'dairy':ti,ab OR 'milk':ti,ab OR 'yogurt':ti,ab OR 'cheese':ti,ab OR 'sea food'/exp OR 'fish':ti,ab OR 'seafood':ti,ab OR 'meat'/exp OR 'meat':ti,ab OR 'poultry':ti,ab OR 'olive oil'/exp OR 'olive oil':ti,ab OR 'alcohol'/exp OR 'alcohol*':ti,ab OR 'wine':ti,ab) AND ('sleep'/exp OR 'sleep disorder'/exp OR 'sleep*':ti,ab OR 'insomnia*':ti,ab OR 'dyssomnia*':ti,ab OR 'parasomnia*':ti,ab OR 'somnolence':ti,ab OR 'sleep quality':ti,ab OR 'sleep duration':ti,ab) AND ([article]/lim OR [review]/lim)",
    "# Micro-variant 2 (Field/Scope-based): Balanced + Title restriction",
    "('Mediterranean diet':ti OR 'MedDiet':ti OR 'fruit*':ti OR 'vegetable*':ti OR 'cereal*':ti OR 'legume*':ti OR 'dairy':ti OR 'fish':ti OR 'meat':ti OR 'olive oil':ti OR 'alcohol*':ti) AND ('sleep*':ti OR 'insomnia*':ti)",
    "# Micro-variant 3 (Proximity-based): Balanced + ADJ5",
    "('Mediterranean diet':ti,ab OR 'fruit':ti,ab OR 'vegetable':ti,ab OR 'cereal':ti,ab OR 'legume':ti,ab OR 'dairy':ti,ab OR 'fish':ti,ab OR 'meat':ti,ab OR 'olive oil':ti,ab OR 'alcohol':ti,ab) ADJ5 ('sleep':ti,ab OR 'insomnia':ti,ab)"
  ]
}
```
## 3. PRESS Self-Check (JSON Patch)
```json
{
  "json_patch": {}
}
```

## Translation Notes
- **Med Diet**: MeSH `Diet, Mediterranean` vs Emtree `Mediterranean diet`.
- **Sleep**: Broad coverage across all databases.
- **Date Filters**: Applied inline for PubMed/Scopus/WoS; omitted for Embase as requested.
