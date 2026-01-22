**After defining the Research Question Using PICO/PECOS Framework**

## 2. Identify Key Concepts and Develop Synonym Lists
For each PICO element, researchers brainstorm all possible ways that concept might be described:
Thinking process example (for "myocardial infarction"):

What are the medical terms? → myocardial infarction, MI, acute coronary syndrome
What are lay terms? → heart attack
What are related conditions? → STEMI, NSTEMI, acute myocardial infarction
What are abbreviations? → AMI
What are older/alternative terms? → coronary thrombosis
Are there spelling variations? → British vs American spelling

This is done systematically by:

Reviewing key papers already known in the field
Consulting medical subject heading (MeSH) trees in PubMed
Consulting Emtree terms in Embase
Reading review articles to see terminology used
Consulting with content experts
Examining index terms from relevant articles

## 3. Build Search Blocks for Each Concept
Researchers create separate "blocks" for each main concept, using Boolean operators:
Block structure:

Use OR to combine synonyms within a concept (increases sensitivity)
Use AND to combine different concepts (increases specificity)

## Example for a smoking and lung cancer query:
Block 1 (Exposure - Smoking):
smoking OR smoker* OR tobacco OR cigarette* OR "tobacco use"

Block 2 (Outcome - Lung cancer):
"lung cancer" OR "lung neoplasm*" OR "pulmonary neoplasm*" OR "bronchogenic carcinoma"

Final query: Block 1 AND Block 2

## 4. Use Controlled Vocabulary and Free Text

Researchers use a **dual approach**:

**Controlled vocabulary (MeSH terms, Emtree):**
- These are standardized indexing terms assigned by database curators
- Advantage: Captures articles regardless of author's word choice
- Disadvantage: Takes time for new articles to be indexed; indexing may be inconsistent

**Free text searching:**
- Searches title, abstract, and sometimes full text for your exact terms
- Advantage: Captures very recent articles; captures specific terminology
- Disadvantage: Misses articles using different terminology

**Best practice:** Combine both approaches with OR to maximize sensitivity.

Example:
```
("Diabetes Mellitus, Type 2"[MeSH] OR "type 2 diabetes" OR "diabetes mellitus" OR T2DM OR NIDDM)
```

## 5. Use Truncation and Wildcards Strategically

**Truncation (*)** captures word variations:
- `child*` finds: child, children, childhood, childish
- `smok*` finds: smoke, smoking, smoker, smoked

**Thinking process:** Where would truncation help vs. hurt?
- Helpful: `diabete*` captures diabetes, diabetic, diabetics
- Potentially problematic: `can*` captures cancer but also can, canal, canine

**Wildcards (?, $, #)** handle spelling variations:
- `wom?n` finds woman, women
- `randomi?ed` finds randomized, randomised

## 6. Use Phrase Searching and Proximity Operators

**Phrase searching (""):**
- `"heart failure"` ensures words appear together in that order
- Prevents retrieval of unrelated articles mentioning "heart" and "failure" separately

**Proximity operators (NEAR, ADJ, W/):**
- `diabetes NEAR/3 management` finds these words within 3 words of each other
- Useful for concepts that might be expressed in different word orders


## 7. Apply Methodological Filters (When Appropriate)

For specific study designs, researchers may add validated filters:

**Example RCT filter components:**
```
randomized controlled trial[pt] OR controlled clinical trial[pt] OR randomized[tiab] OR placebo[tiab] OR "clinical trials as topic"[mesh:noexp] OR randomly[tiab] OR trial[ti]
```

**Caution:** Filters reduce sensitivity. The thinking here is: Do I need to restrict by study design now, or should I do this during screening?

For systematic reviews, most researchers prefer **high sensitivity** at the search stage and filter during title/abstract screening.

## 8. Adapt Queries Across Multiple Databases

Each database has different syntax and indexing:

**PubMed/MEDLINE:**
- Uses MeSH terms
- Syntax: `[MeSH]`, `[tiab]` for title/abstract

**Embase:**
- Uses Emtree terms
- Often has more drug and European literature
- Syntax: `/exp` for exploded terms

**CINAHL:**
- Nursing and allied health focus
- Uses CINAHL headings

**Web of Science/Scopus:**
- No controlled vocabulary
- Citation searching is valuable here

**Thinking process:** Don't just copy-paste queries. Translate the search strategy concept-by-concept, using each database's specific features.


