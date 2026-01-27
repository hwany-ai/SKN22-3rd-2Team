# 📊 데이터 수집 및 전처리 보고서

> **Patent Guard v2.0 - AI 특허 선행 기술 조사 시스템**  
> 작성일: 2026-01-27

---

## 1. 데이터 수집 개요

### 1.1 데이터 소스

| 항목 | 내용 |
|------|------|
| **소스** | Google Patents Public Dataset |
| **저장소** | Google BigQuery (`patents-public-data.patents.publications`) |
| **접근 방식** | BigQuery SQL 쿼리 |
| **비용** | ~$2 USD (390GB 스캔) |

### 1.2 수집 기준

| 항목 | 설정값 |
|------|--------|
| **기간** | 2018-01-01 ~ 2024-12-31 |
| **국가** | US, EP, WO, CN, JP, KR |
| **수집량** | 10,000건 |

### 1.3 도메인 키워드

```
AI/NLP 도메인 키워드:
- retrieval augmented generation
- large language model
- neural information retrieval
- semantic search
- document embedding
- transformer attention
- knowledge graph reasoning
- prompt engineering
- context window
- fine-tuning language model
- quantization neural network
- efficient inference
- multi-modal retrieval
```

### 1.4 IPC 분류 코드

| IPC 코드 | 분류 |
|----------|------|
| G06F 16 | Information Retrieval |
| G06F 40 | Natural Language Processing |
| G06N 3 | Neural Networks |
| G06N 5 | Knowledge-based Systems |
| G06N 20 | Machine Learning |
| H04L 12 | Data Switching Networks |

---

## 2. 수집된 데이터 현황

### 2.1 원본 데이터 (Raw Data)

| 파일명 | 크기 | 건수 |
|--------|------|------|
| `patents_10k.json` | 74 MB | 10,000건 |

### 2.2 전처리 데이터 (Processed Data)

| 파일명 | 크기 | 건수 |
|--------|------|------|
| `processed_patents_10k.json` | 61 MB | 10,000건 |

### 2.3 데이터 필드 구조

```json
{
  "publication_number": "US-12345678-A1",
  "title": "특허 제목",
  "abstract": "특허 초록 텍스트...",
  "claims": [
    {
      "claim_number": 1,
      "claim_type": "independent",
      "claim_text": "청구항 텍스트..."
    }
  ],
  "ipc_codes": ["G06N 3/08", "G06F 40/30"],
  "cited_publications": ["US-98765432-B2"],
  "filing_date": "2023-01-15",
  "assignee": "기업명"
}
```

---

## 3. 전처리 과정

### 3.1 전처리 파이프라인

```
[원본 데이터]
     ↓
[1] 텍스트 정규화
     - 특수문자 처리
     - 공백 정리
     - 인코딩 통일 (UTF-8)
     ↓
[2] 청구항 파싱
     - 독립항/종속항 분류
     - 청구항 번호 추출
     - 청구항 텍스트 정리
     ↓
[3] 청킹 (Chunking)
     - 최대 1024 토큰 단위 분할
     - 오버랩 128 토큰
     ↓
[4] 메타데이터 추가
     - IPC 코드 정규화
     - 날짜 포맷 통일
     ↓
[전처리 완료 데이터]
```

### 3.2 전처리 통계

| 항목 | 수치 |
|------|------|
| 원본 특허 수 | 10,000건 |
| 전처리 완료 | 10,000건 |
| 추출된 청구항 | ~30,000개 |
| 생성된 청크 | ~200,000개 |
| 평균 Abstract 길이 | 약 300 단어 |

### 3.3 품질 검증

| 검증 항목 | 결과 |
|-----------|------|
| NULL 값 비율 | < 5% |
| 영어 Abstract 보유율 | ~70% |
| 청구항 파싱 성공률 | ~90% |
| IPC 코드 보유율 | 100% |

---

## 4. 데이터 활용 계획

### 4.1 Self-RAG 분석용

```
사용자 아이디어 입력
     ↓
HyDE (가상 청구항 생성)
     ↓
벡터 검색 (10K 특허 중 Top-5)
     ↓
관련성 평가 (Grading)
     ↓
상세 분석 (유사도/침해/회피)
```

### 4.2 데이터 제한 사항

| 항목 | 내용 |
|------|------|
| **샘플 크기** | 10,000건 (전체 특허의 <0.01%) |
| **용도** | 데모/프로토타입용 |
| **제한** | 종합적 선행 기술 조사에는 부적합 |

---

## 5. 파일 위치

```
SKN22-3rd-2Team/
├── src/data/
│   ├── raw/
│   │   └── patents_10k.json            # 원본 데이터
│   ├── processed/
│   │   └── processed_patents_10k.json  # 전처리 데이터
│   └── sql/
│       └── extraction_AI_NLP_Search_*.sql  # 추출 쿼리
└── 01_data_preprocessing/
    └── README.md                        # 본 보고서
```

---

## 6. 실행 방법

### 데이터 추출 (BigQuery)

```bash
python src/pipeline.py --limit 10000 --execute
```

### 전처리만 실행

```bash
python src/preprocessor.py src/data/raw/patents_10k.json
```

---

## 7. 참고 자료

- [Google Patents Public Dataset](https://console.cloud.google.com/marketplace/product/google_patents_public_datasets/google-patents-public-data)
- [BigQuery 가격 정책](https://cloud.google.com/bigquery/pricing)

---

*작성: Patent Guard Team - 뀨💕*
