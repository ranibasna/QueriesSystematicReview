 DATABASES="pubmed,scopus" ./run_workflow_sleep_apnea.sh
--- Running Query Evaluation and Selection for study: sleep_apnea ---
[INFO] Using queries from studies/sleep_apnea/queries_scopus.txt for provider 'scopus'.
[INFO] Scopus date filter disabled (SCOPUS_SKIP_DATE_FILTER=true or flag). Running query without PUBYEAR bounds.
[WARN] Provider 'scopus' failed: Scopus API returned 401 Unauthorized (key hint 2e47…36c7). This usually means the API key lacks Scopus Search entitlements or requires an Insttoken. Server response: {"service-error":{"status":{"statusCode":"AUTHENTICATION_ERROR","statusText":"Institution Token is not associated with API Key"}}}. Skipping its contribution for this query.
Candidate: 78b5f660  Results=237  Coverage=0.50  Score=1.047
[INFO] Scopus date filter disabled (SCOPUS_SKIP_DATE_FILTER=true or flag). Running query without PUBYEAR bounds.
[WARN] Provider 'scopus' failed: Scopus API returned 401 Unauthorized (key hint 2e47…36c7). This usually means the API key lacks Scopus Search entitlements or requires an Insttoken. Server response: {"service-error":{"status":{"statusCode":"AUTHENTICATION_ERROR","statusText":"Institution Token is not associated with API Key"}}}. Skipping its contribution for this query.
Candidate: 211809ff  Results=543  Coverage=0.50  Score=1.109
[INFO] Scopus date filter disabled (SCOPUS_SKIP_DATE_FILTER=true or flag). Running query without PUBYEAR bounds.
[WARN] Provider 'scopus' failed: Scopus API returned 401 Unauthorized (key hint 2e47…36c7). This usually means the API key lacks Scopus Search entitlements or requires an Insttoken. Server response: {"service-error":{"status":{"statusCode":"AUTHENTICATION_ERROR","statusText":"Institution Token is not associated with API Key"}}}. Skipping its contribution for this query.
Candidate: 5befb2fe  Results=479  Coverage=0.50  Score=1.096
[INFO] Scopus date filter disabled (SCOPUS_SKIP_DATE_FILTER=true or flag). Running query without PUBYEAR bounds.
[WARN] Provider 'scopus' failed: Scopus API returned 401 Unauthorized (key hint 2e47…36c7). This usually means the API key lacks Scopus Search entitlements or requires an Insttoken. Server response: {"service-error":{"status":{"statusCode":"AUTHENTICATION_ERROR","statusText":"Institution Token is not associated with API Key"}}}. Skipping its contribution for this query.
Candidate: 4a359cb4  Results=481  Coverage=0.50  Score=1.096
[INFO] Scopus date filter disabled (SCOPUS_SKIP_DATE_FILTER=true or flag). Running query without PUBYEAR bounds.
[WARN] Provider 'scopus' failed: Scopus API returned 401 Unauthorized (key hint 2e47…36c7). This usually means the API key lacks Scopus Search entitlements or requires an Insttoken. Server response: {"service-error":{"status":{"statusCode":"AUTHENTICATION_ERROR","statusText":"Institution Token is not associated with API Key"}}}. Skipping its contribution for this query.
Candidate: dec5aae4  Results=308  Coverage=0.50  Score=1.062

Best query: 211809ff  Score=1.109  Results=543  Coverage=0.5
Wrote: sealed_outputs/sleep_apnea/sealed_20251119-084501.json
Summary: sealed_outputs/sleep_apnea/selection_summary_20251119-084501.csv
[INFO] Using queries from studies/sleep_apnea/queries_scopus.txt for provider 'scopus'.
[INFO] Scopus date filter disabled (SCOPUS_SKIP_DATE_FILTER=true or flag). Running query without PUBYEAR bounds.
[WARN] Provider 'scopus' failed: Scopus API returned 401 Unauthorized (key hint 2e47…36c7). This usually means the API key lacks Scopus Search entitlements or requires an Insttoken. Server response: {"service-error":{"status":{"statusCode":"AUTHENTICATION_ERROR","statusText":"Institution Token is not associated with API Key"}}}. Skipping its contribution for this query.
Query[78b5f660]: results=285  TP=7  recall=0.636  NNR_proxy=40.71
[INFO] Scopus date filter disabled (SCOPUS_SKIP_DATE_FILTER=true or flag). Running query without PUBYEAR bounds.
[WARN] Provider 'scopus' failed: Scopus API returned 401 Unauthorized (key hint 2e47…36c7). This usually means the API key lacks Scopus Search entitlements or requires an Insttoken. Server response: {"service-error":{"status":{"statusCode":"AUTHENTICATION_ERROR","statusText":"Institution Token is not associated with API Key"}}}. Skipping its contribution for this query.
Query[211809ff]: results=717  TP=6  recall=0.545  NNR_proxy=119.50
[INFO] Scopus date filter disabled (SCOPUS_SKIP_DATE_FILTER=true or flag). Running query without PUBYEAR bounds.
[WARN] Provider 'scopus' failed: Scopus API returned 401 Unauthorized (key hint 2e47…36c7). This usually means the API key lacks Scopus Search entitlements or requires an Insttoken. Server response: {"service-error":{"status":{"statusCode":"AUTHENTICATION_ERROR","statusText":"Institution Token is not associated with API Key"}}}. Skipping its contribution for this query.
Query[5befb2fe]: results=634  TP=6  recall=0.545  NNR_proxy=105.67
[INFO] Scopus date filter disabled (SCOPUS_SKIP_DATE_FILTER=true or flag). Running query without PUBYEAR bounds.
[WARN] Provider 'scopus' failed: Scopus API returned 401 Unauthorized (key hint 2e47…36c7). This usually means the API key lacks Scopus Search entitlements or requires an Insttoken. Server response: {"service-error":{"status":{"statusCode":"AUTHENTICATION_ERROR","statusText":"Institution Token is not associated with API Key"}}}. Skipping its contribution for this query.
Query[4a359cb4]: results=633  TP=6  recall=0.545  NNR_proxy=105.50
[INFO] Scopus date filter disabled (SCOPUS_SKIP_DATE_FILTER=true or flag). Running query without PUBYEAR bounds.
[WARN] Provider 'scopus' failed: Scopus API returned 401 Unauthorized (key hint 2e47…36c7). This usually means the API key lacks Scopus Search entitlements or requires an Insttoken. Server response: {"service-error":{"status":{"statusCode":"AUTHENTICATION_ERROR","statusText":"Institution Token is not associated with API Key"}}}. Skipping its contribution for this query.
Query[dec5aae4]: results=400  TP=6  recall=0.545  NNR_proxy=66.67
Saved: benchmark_outputs/sleep_apnea/summary_20251119-084551.csv
Saved: benchmark_outputs/sleep_apnea/details_20251119-084551.json
Final metrics: {
  "TP": 4,
  "Retrieved": 543,
  "Gold": 11,
  "Precision": 0.007366482504604052,
  "Recall": 0.36363636363636365,
  "F1": 0.014440433212996392,
  "Jaccard": 0.007272727272727273,
  "OverlapCoeff": 0.36363636363636365
}
Wrote: final_outputs/sleep_apnea/final_20251119-084501.json
--- Query Evaluation and Selection Complete ---

--- Running Query Aggregation and Comparison for study: sleep_apnea ---
Wrote aggregates in aggregates/sleep_apnea
--- Query Aggregation and Comparison Complete ---

--- Running Score Aggregated Sets for study: sleep_apnea ---
Set[consensus_k2]: n=72 TP=3 Precision=0.042 Recall=0.273 F1=0.072
Set[precision_gated_union]: n=1176 TP=10 Precision=0.009 Recall=0.909 F1=0.017
Set[time_stratified_hybrid]: n=1176 TP=10 Precision=0.009 Recall=0.909 F1=0.017
Set[two_stage_screen]: n=141 TP=4 Precision=0.028 Recall=0.364 F1=0.053
Set[weighted_vote]: n=1176 TP=10 Precision=0.009 Recall=0.909 F1=0.017
Saved: aggregates_eval/sleep_apnea/sets_summary_20251119-084553.csv
Saved: aggregates_eval/sleep_apnea/sets_details_20251119-084553.json
--- Score Aggregated Sets Complete ---
