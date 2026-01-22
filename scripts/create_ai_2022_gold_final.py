#!/usr/bin/env python3
"""
Create verified Gold Standard PMID list for ai_2022.

These PMIDs are extracted from Ai et al. 2022 "Blood pressure and childhood 
obstructive sleep apnea: A systematic review and meta-analysis"
(Sleep Medicine Reviews, doi: 10.1016/j.smrv.2022.101663)

The 14 included studies are references [12, 13, 17, 18, 28-37] from the paper.
PMIDs verified against PubMed records.
"""

import csv
import os

# Get script directory and project root
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

# Verified PMIDs from the Ai 2022 systematic review
# Based on Table 1 and references [12, 13, 17, 18, 28-37]
# All PMIDs verified via PubMed search by title on 2026-01-16
GOLD_STANDARD = [
    # Ref 13: Amin RS, Kimball TR, et al. 2004
    # "24-hour ambulatory blood pressure monitoring in children with sleep-disordered breathing"
    # Am J Respir Crit Care Med 2004;169:950-956
    {"pmid": "14764433"},
    
    # Ref 28: Amin R, Somers VK, et al. 2008  
    # "Activity-adjusted 24-hour ambulatory blood pressure and cardiac remodeling"
    # Hypertension 2008;51:84-91
    {"pmid": "18071053"},
    
    # Ref 29: Bixler EO, Vgontzas AN, et al. 2008
    # "Blood pressure associated with sleep-disordered breathing in a population sample of children"
    # Hypertension 2008;52:841-846
    {"pmid": "18838624"},
    
    # Ref 17: Chan KC, Au CT, et al. 2020
    # "Childhood OSA is an independent determinant of blood pressure in adulthood"
    # Thorax 2020;75:422-431
    {"pmid": "32209641"},
    
    # Ref 30: Geng X, Wu Y, et al. 2019
    # "Ambulatory blood pressure monitoring in children with obstructive sleep apnea syndrome"
    # Pediatr Investig 2019;3:217-222
    {"pmid": "32851326"},
    
    # Ref 18: Fernandez-Mendoza J, He F, et al. 2021
    # "Association of Pediatric Obstructive Sleep Apnea With Elevated Blood Pressure and Orthostatic Hypertension"
    # JAMA Cardiol 2021;6:1144-1151
    {"pmid": "34160576"},
    
    # Ref 31: Horne RS, Yang JS, et al. 2011
    # "Elevated blood pressure during sleep and wake in children with sleep-disordered breathing"
    # Pediatrics 2011;128:e85-92
    {"pmid": "21708802"},
    
    # Ref 32: Horne RSC, Ong C, et al. 2020
    # "Are there gender differences in the severity and consequences of sleep disordered in children?"
    # Sleep Med 2020;67:147-155
    {"pmid": "31927221"},
    
    # Ref 33: Kaditis AG, Alexopoulos EI, et al. 2010
    # "Correlation of urinary excretion of sodium with severity of sleep-disordered breathing"
    # Pediatr Pulmonol 2010;45:999-1004
    {"pmid": "20648668"},
    
    # Ref 34: Kang KT, Chiu SN, et al. 2017
    # "Comparisons of office and 24-hour ambulatory blood pressure monitoring in children with OSA"
    # J Pediatr 2017;182:177-183.e2
    {"pmid": "27939257"},
    
    # Ref 12: Li AM, Au CT, et al. 2008
    # "Ambulatory blood pressure in children with obstructive sleep apnoea"
    # Thorax 2008;63:803-809 (not Sleep as stated in paper table)
    {"pmid": "18388205"},
    
    # Ref 35: McConnell K, Somers VK, et al. 2009
    # "Baroreflex gain in children with obstructive sleep apnea"
    # Am J Respir Crit Care Med 2009;180:42-48
    {"pmid": "19286627"},
    
    # Ref 36: O'Driscoll DM, Foster AM, et al. 2009
    # "Acute cardiovascular changes with obstructive events in children with sleep disordered breathing"
    # Sleep 2009;32:1265-1271
    {"pmid": "19848356"},
    
    # Ref 37: O'Driscoll DM, Horne RS, et al. 2011
    # "Increased sympathetic activity in children with obstructive sleep apnea: cardiovascular implications"
    # Sleep Med 2011;12:483-488
    {"pmid": "21521626"},
]

def main():
    output_path = os.path.join(PROJECT_ROOT, "studies", "ai_2022", "gold_pmids_ai_2022.csv")
    
    # Write simple format matching sleep_apnea example
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['pmid'])
        for study in GOLD_STANDARD:
            writer.writerow([study['pmid']])
    
    print(f"✅ Created gold standard file: {output_path}")
    print(f"📊 Total studies: {len(GOLD_STANDARD)}")
    print()
    print("PMIDs:")
    for study in GOLD_STANDARD:
        print(f"  {study['pmid']}")


if __name__ == "__main__":
    main()
