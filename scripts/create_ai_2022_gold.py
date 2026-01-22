#!/usr/bin/env python3
"""
Create the correct Gold Standard PMID list for ai_2022.

Based on manual verification from the paper's reference list (Table 1).
"""

import csv
import os

# The 14 included studies from Table 1 of Ai 2022
# References [12, 13, 17, 18, 28-37] with verified PMIDs

GOLD_STANDARD = [
    # Ref 13: Amin RS et al. 2004 - "24-hour ambulatory blood pressure monitoring in children with sleep-disordered breathing"
    {"pmid": "15347546", "first_author": "Amin", "year": "2004"},
    
    # Ref 28: Amin R et al. 2008 - "Activity-adjusted 24-hour ambulatory blood pressure and cardiac remodeling"
    {"pmid": "18071053", "first_author": "Amin", "year": "2008"},
    
    # Ref 29: Bixler EO et al. 2008 - "Blood pressure associated with sleep-disordered breathing in a population sample of children"
    {"pmid": "18838624", "first_author": "Bixler", "year": "2008"},
    
    # Ref 17: Chan KC et al. 2020 - "Childhood OSA is an independent determinant of blood pressure in adulthood" (Thorax)
    {"pmid": "32094252", "first_author": "Chan", "year": "2020"},
    
    # Ref 30: Geng X et al. 2019 - "Ambulatory blood pressure monitoring in children with obstructive sleep apnea syndrome"
    {"pmid": "32851326", "first_author": "Geng", "year": "2019"},
    
    # Ref 18: Fernandez-Mendoza J et al. 2021 - "Association of Pediatric OSA With Elevated BP and Orthostatic Hypertension"
    {"pmid": "34160576", "first_author": "Fernandez-Mendoza", "year": "2021"},
    
    # Ref 31: Horne RS et al. 2011 - "Elevated blood pressure during sleep and wake in children with sleep-disordered breathing"
    {"pmid": "21708806", "first_author": "Horne", "year": "2011"},
    
    # Ref 32: Horne RSC et al. 2020 - "Are there gender differences in the severity and consequences of sleep disordered in children?"
    {"pmid": "31927221", "first_author": "Horne", "year": "2020"},
    
    # Ref 33: Kaditis AG et al. 2010 - "Correlation of urinary excretion of sodium with severity of sleep-disordered breathing"
    {"pmid": "20648668", "first_author": "Kaditis", "year": "2010"},
    
    # Ref 34: Kang KT et al. 2017 - "Comparisons of office and 24-hour ambulatory blood pressure monitoring in children with OSA"
    {"pmid": "28159417", "first_author": "Kang", "year": "2017"},
    
    # Ref 12: Li AM et al. 2008 - "Ambulatory blood pressure in children with obstructive sleep apnoea"
    {"pmid": "18714778", "first_author": "Li", "year": "2008"},
    
    # Ref 35: McConnell K et al. 2009 - "Baroreflex gain in children with obstructive sleep apnea"
    {"pmid": "19286627", "first_author": "McConnell", "year": "2009"},
    
    # Ref 36: O'Driscoll DM et al. 2009 - "Acute cardiovascular changes with obstructive events in children"
    {"pmid": "19848356", "first_author": "O'Driscoll", "year": "2009"},
    
    # Ref 37: O'Driscoll DM et al. 2011 - "Increased sympathetic activity in children with obstructive sleep apnea"
    {"pmid": "21521626", "first_author": "O'Driscoll", "year": "2011"},
]


def main():
    # Get project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    output_path = os.path.join(project_root, "studies", "ai_2022", "gold_pmids_ai_2022.csv")
    
    # Write the gold standard CSV
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['pmid', 'first_author', 'year'])
        writer.writeheader()
        writer.writerows(GOLD_STANDARD)
    
    print(f"✅ Created gold standard file: {output_path}")
    print(f"📊 Total studies: {len(GOLD_STANDARD)}")
    print()
    print("PMIDs:")
    for study in GOLD_STANDARD:
        print(f"  {study['pmid']} - {study['first_author']} ({study['year']})")


if __name__ == "__main__":
    main()
