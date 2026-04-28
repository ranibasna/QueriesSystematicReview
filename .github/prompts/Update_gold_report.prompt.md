---
name: Update_gold_report
description: "Update the study gold_generation_report with results, issues, and workflow notes"
agent: agent
---

<!-- Tip: Use /create-prompt in chat to generate content with agent assistance -->

Can you update the corresponding study `gold_generation_report` markdown file with the results and any note, issue, or challenge related to the gold extraction that may affect the result. Use a datestamp if needed.

- Check the corresponding Embase query 1 file, `embase_query1`. If it has 0 records, then the query returned a huge number of articles and I did not include it in the study, so report that as well in the corresponding `gold_generation_report`.

- Also document any other important points that were raised or happened during the end-to-end process of getting the scores.