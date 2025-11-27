# Web of Science Integration - Quick Start Guide

## 🚀 Ready to Test in 3 Steps

### Step 1: Set Your API Key (30 seconds)

Open your `.env` file and add:
```bash
WOS_API_KEY=your_actual_api_key_here
```

Or set it temporarily in terminal:
```bash
export WOS_API_KEY="your_actual_api_key_here"
```

### Step 2: Test Connection (1 minute)

```bash
conda activate systematic_review_queries
python test_wos_connection.py
```

**Expected**: Green checkmark ✓ and sample results

**If error**: See troubleshooting in `wos_implementation_summary.md`

### Step 3: Run Workflow (5-10 minutes)

```bash
python llm_sr_select_and_score.py \
  --databases pubmed,scopus,wos \
  --study-name sleep_apnea \
  select \
  --mindate 2020/01/01 \
  --maxdate 2021/12/31 \
  --concept-terms concept_terms_sleep_apnea.csv \
  --queries-txt queries.txt \
  --outdir sealed_outputs/sleep_apnea
```

**Look for**:
- ✅ "Web of Science: X results" in console
- ✅ "Deduplication: X raw → Y unique"
- ✅ No errors or exceptions

---

## 📊 What to Expect

**With 2 databases** (PubMed + Scopus):
- Sleep apnea: ~3,500 unique articles
- Duplicates: ~7%

**With 3 databases** (PubMed + Scopus + WoS):
- Expected: ~4,200-4,500 unique articles
- Duplicates: ~15-20%
- **Gain**: +20-25% coverage! 🎉

---

## 🔧 Files Created

1. ✨ **`search_providers.py`** - Full WoS provider (180 lines)
2. ✨ **`studies/sleep_apnea/queries_wos.txt`** - WoS-specific queries
3. ✨ **`test_wos_connection.py`** - Quick API test
4. ✨ **`sr_config.toml`** - WoS configuration

---

## 🐛 Quick Troubleshooting

**401 Unauthorized?**
- Check API key in [Developer Portal](https://developer.clarivate.com/)
- Verify WoS Starter API subscription is active

**429 Rate Limit?**
- Wait 5 minutes and retry
- Already rate-limited at 0.5s per request

**No results?**
- Run `test_wos_connection.py` first
- Check query syntax in `queries_wos.txt`

---

## 📖 Full Documentation

See `wos_implementation_summary.md` for:
- Complete implementation details
- Comprehensive troubleshooting
- Architecture notes
- Next steps

---

## ✅ Implementation Status

- [x] WebOfScienceProvider class complete
- [x] Configuration integrated
- [x] Query files created
- [x] Test script ready
- [ ] **→ YOU ARE HERE: Ready to test with real API key**
- [ ] Verify results with real data
- [ ] Update README with WoS instructions
- [ ] Create final session summary

---

**Time to test**: 5 minutes  
**Status**: Ready for real API testing 🚀
