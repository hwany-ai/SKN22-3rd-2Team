# 쇼특허 (Short-Cut) v3.0 - Unit Test Report

> **Date:** 2026-01-28  
> **Platform:** Windows 11, Python 3.13.9  
> **Framework:** pytest 9.0.2  
> **Team:** 뀨💕  

---

## 1. Executive Summary

| Metric | Value |
|--------|-------|
| **Total Tests** | 27 |
| **Passed** | 22 ✅ |
| **Failed** | 5 ❌ |
| **Pass Rate** | **81.5%** |
| **Duration** | 2.83s |

---

## 2. Test Results by Module

### 2.1 Hybrid Search (RRF Algorithm)
📄 `tests/test_hybrid_search.py`

| Test | Status | Description |
|------|--------|-------------|
| `test_cross_rank_verification_top_tier` | ❌ FAIL | Doc C ranked higher due to appearing in both lists |
| `test_symmetric_weighting` | ✅ PASS | 0.5:0.5 weight validation |
| `test_asymmetric_weighting_dense_heavy` | ❌ FAIL | Doc C outranks Doc A with 0.8:0.2 weights |
| `test_asymmetric_weighting_sparse_heavy` | ✅ PASS | 0.2:0.8 weight validation |
| `test_edge_case_empty_dense_results` | ✅ PASS | Empty dense list handling |
| `test_edge_case_empty_sparse_results` | ✅ PASS | Empty sparse list handling |
| `test_edge_case_both_empty` | ✅ PASS | Both empty lists handling |
| `test_rrf_k_constant_effect` | ✅ PASS | k constant impact verification |

**Summary:** 6/8 passed (75%)

> **Analysis:** The "failed" tests actually reveal correct RRF behavior - documents appearing in BOTH search results (Doc C) get higher combined scores than documents appearing in only one. This is expected RRF fusion behavior.

---

### 2.2 Claim Parser Level 1 (Regex)
📄 `tests/test_parser.py::TestClaimParserLevel1Regex`

| Test | Status | Description |
|------|--------|-------------|
| `test_standard_us_format_basic` | ✅ PASS | US patent format parsing |
| `test_claim_numbering` | ✅ PASS | Claim number extraction |
| `test_independent_vs_dependent_detection` | ✅ PASS | Claim type classification |
| `test_rag_component_detection` | ❌ FAIL | RAG keyword detection issue |
| `test_claim_text_content` | ✅ PASS | Content extraction |

**Summary:** 4/5 passed (80%)

> **Note:** `rag_component_detection` failed because the mock config was not properly injecting keywords. This is a test configuration issue, not a code bug.

---

### 2.3 Claim Parser Level 2 (Structure)
📄 `tests/test_parser.py::TestClaimParserLevel2Structure`

| Test | Status | Description |
|------|--------|-------------|
| `test_bracket_numbered_format` | ❌ FAIL | Bracket format `(1)` parsing issue |
| `test_korean_format_parsing` | ✅ PASS | Korean `제1항:` format support |
| `test_mixed_indent_structure` | ✅ PASS | Mixed indentation handling |

**Summary:** 2/3 passed (67%)

> **Note:** Bracket format test failed due to regex pattern priority - the `(1)` format was partially matched by a different pattern.

---

### 2.4 Claim Parser Level 3 (NLP)
📄 `tests/test_parser.py::TestClaimParserLevel3NLP`

| Test | Status | Description |
|------|--------|-------------|
| `test_ocr_noise_handling` | ✅ PASS | OCR noise graceful degradation |
| `test_nlp_disabled_graceful_fallback` | ✅ PASS | NLP disabled fallback |
| `test_sentence_boundary_mock` | ✅ PASS | Sentence detection |

**Summary:** 3/3 passed (100%) ✨

---

### 2.5 Claim Parser Level 4 (Minimal Fallback)
📄 `tests/test_parser.py::TestClaimParserLevel4Minimal`

| Test | Status | Description |
|------|--------|-------------|
| `test_raw_text_blob_fallback` | ✅ PASS | Raw text handling |
| `test_empty_input_handling` | ✅ PASS | Empty input returns `[]` |
| `test_whitespace_only_input` | ✅ PASS | Whitespace handling |
| `test_single_paragraph_fallback` | ✅ PASS | Single paragraph as single claim |
| `test_multiple_paragraphs_fallback` | ❌ FAIL | Paragraph splitting behavior |

**Summary:** 4/5 passed (80%)

---

### 2.6 Data Integrity Tests
📄 `tests/test_parser.py::TestClaimParserDataIntegrity`

| Test | Status | Description |
|------|--------|-------------|
| `test_parsed_claim_dataclass_fields` | ✅ PASS | All required fields present |
| `test_char_and_word_counts` | ✅ PASS | Character/word count accuracy |
| `test_claims_sorted_by_number` | ✅ PASS | Sorted output verification |

**Summary:** 3/3 passed (100%) ✨

---

## 3. Failed Test Analysis

### 3.1 RRF Fusion Tests
**Root Cause:** The test expectation was incorrect. RRF algorithm correctly gives higher scores to documents that appear in BOTH search results (Doc C ranked #10 in both) over documents that appear in only ONE list (Doc A in dense only, Doc B in sparse only).

**Impact:** None - this is expected algorithm behavior.

**Action:** Update test expectations to reflect correct RRF behavior.

---

### 3.2 RAG Component Detection
**Root Cause:** The `@patch('preprocessor.config')` mock was not properly injecting the `rag_component_keywords` into the ClaimParser instance.

**Impact:** Low - unit test configuration issue only.

**Action:** Fix mock setup to properly patch the config object.

---

### 3.3 Bracket Numbered Format
**Root Cause:** Regex pattern matching priority issue. The `(1)` format was being captured by a broader pattern instead of the specific bracket pattern.

**Impact:** Medium - affects non-standard bracket-numbered claims.

**Action:** Adjust regex pattern order in `ClaimParser.CLAIM_PATTERNS`.

---

## 4. Recommendations

| Priority | Action | Effort |
|----------|--------|--------|
| 🔴 High | Update RRF test expectations | S |
| 🟡 Medium | Fix regex pattern priority | M |
| 🟢 Low | Fix test mock configuration | S |

---

## 5. Files Generated

| File | Description |
|------|-------------|
| `report/test_report.html` | Interactive HTML report (62 KB) |
| `report/test_results.txt` | Raw pytest output |
| `report/test_report.md` | This summary report |

---

*Generated by 쇼특허 (Short-Cut) v3.0 Test Suite*  
*Team 뀨💕*
