"""
Patent Guard v2.0 - Configuration Module (Antigravity Edition)
================================================================
Lightweight configuration for OpenAI API + FAISS in-memory architecture.

Author: Patent Guard Team
License: MIT
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()


# =============================================================================
# Project Paths
# =============================================================================

PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
TRIPLETS_DIR = DATA_DIR / "triplets"
EMBEDDINGS_DIR = DATA_DIR / "embeddings"
INDEX_DIR = DATA_DIR / "index"

# Create directories if they don't exist
for dir_path in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, TRIPLETS_DIR, EMBEDDINGS_DIR, INDEX_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)


# =============================================================================
# BigQuery Configuration
# =============================================================================

@dataclass
class BigQueryConfig:
    """BigQuery connection and query configuration."""
    
    # GCP Project ID (set via environment variable or override here)
    project_id: str = os.environ.get("GCP_PROJECT_ID", "your-gcp-project-id")
    
    # Dataset and table
    dataset: str = "patents-public-data.patents"
    publications_table: str = "publications"  # Full table (~1.4TB scan cost)
    
    # Date range for filtering (cost optimization)
    min_filing_date: str = "2018-01-01"  # Focus on recent patents
    max_filing_date: str = "2024-12-31"
    
    # Batch processing
    batch_size: int = 1000
    max_results: Optional[int] = None  # None = no limit
    
    # Cost optimization
    dry_run: bool = True  # Set to True to check query cost first
    use_query_cache: bool = True
    
    @property
    def full_table_name(self) -> str:
        return f"`{self.dataset}.{self.publications_table}`"


# =============================================================================
# Domain Keywords Configuration
# =============================================================================

@dataclass
class DomainConfig:
    """Technical domain keywords and IPC/CPC codes for filtering."""
    
    # Primary domain name
    domain_name: str = "AI_NLP_Search"
    
    # Search keywords (OR logic) - Broader for more results
    keywords: List[str] = field(default_factory=lambda: [
        # Information retrieval (broad)
        "information retrieval",
        "document retrieval",
        "semantic search",
        "text search",
        
        # NLP/AI core
        "natural language processing",
        "machine learning",
        "neural network",
        "deep learning",
        
        # Embedding/Vector
        "word embedding",
        "text embedding",
        "vector representation",
        
        # Question answering
        "question answering",
        "knowledge base",
    ])
    
    # IPC/CPC Classification Codes
    ipc_codes: List[str] = field(default_factory=lambda: [
        "G06F 16",    # Information retrieval; Database structures
        "G06F 40",    # Natural language processing
        "G06N 3",     # Artificial intelligence - Neural networks
        "G06N 5",     # AI - Knowledge processing
        "G06N 20",    # Machine learning
        "H04L 12",    # Data switching networks (for distributed ML)
    ])
    
    # RAG-specific component keywords for tagging
    rag_component_keywords: List[str] = field(default_factory=lambda: [
        "retriever",
        "generator",
        "reranker",
        "re-ranker",
        "dense passage",
        "sparse retrieval",
        "hybrid retrieval",
        "knowledge base",
        "vector store",
        "embedding index",
        "semantic similarity",
        "context window",
        "chunking",
        "document encoder",
        "query encoder",
    ])


# =============================================================================
# Embedding Model Configuration (OpenAI API)
# =============================================================================

@dataclass
class EmbeddingConfig:
    """OpenAI Embedding configuration."""
    
    # Model - OpenAI text-embedding-3-small
    model_id: str = "text-embedding-3-small"
    embedding_dim: int = 1536  # OpenAI dimension
    max_context_length: int = 8191  # text-embedding-3-small limit
    
    # API settings
    api_key: str = os.environ.get("OPENAI_API_KEY", "")
    
    # Batch processing (OpenAI has 2048 texts per batch limit)
    batch_size: int = 100
    
    # Rate limiting
    requests_per_minute: int = 3000  # OpenAI tier limit
    tokens_per_minute: int = 1_000_000
    
    # Weighting for hybrid indexing
    title_weight: float = 1.5      # Higher weight for titles
    claim_weight: float = 2.0      # Highest weight for claims  
    abstract_weight: float = 1.2   # Medium weight for abstracts
    description_weight: float = 1.0  # Base weight for descriptions


# =============================================================================
# FAISS Vector Database Configuration
# =============================================================================

@dataclass
class FaissConfig:
    """FAISS in-memory vector database configuration."""
    
    # Index file paths
    index_path: Path = field(default_factory=lambda: INDEX_DIR / "patent_index.bin")
    metadata_path: Path = field(default_factory=lambda: INDEX_DIR / "patent_metadata.pkl")
    
    # Index type
    # - "Flat": Exact search (best for < 100K vectors)
    # - "IVF": Approximate search (for larger datasets)
    index_type: str = "Flat"
    
    # Search configuration
    top_k_default: int = 10
    
    # For IVF indexes (not used with Flat)
    nlist: int = 100  # Number of clusters
    nprobe: int = 10  # Number of clusters to search


# =============================================================================
# PAI-NET Triplet Configuration
# =============================================================================

@dataclass
class PAINETConfig:
    """PAI-NET triplet generation configuration."""
    
    # Triplet generation
    min_citations_for_anchor: int = 3  # Minimum citations to be an anchor
    negatives_per_positive: int = 5    # Number of negatives per positive pair
    
    # Negative sampling strategy
    hard_negative_ratio: float = 0.3   # 30% hard negatives (same IPC, no citation)
    random_negative_ratio: float = 0.7 # 70% random negatives
    
    # Output format
    output_format: str = "jsonl"  # jsonl or parquet


# =============================================================================
# Self-RAG Configuration
# =============================================================================

@dataclass
class SelfRAGConfig:
    """Self-RAG analysis configuration using OpenAI."""
    
    # OpenAI API for analysis
    openai_model: str = "gpt-4o-mini"  # Cost-effective, fast
    openai_api_key: str = os.environ.get("OPENAI_API_KEY", "")
    
    # Critique prompt template
    critique_prompt_template: str = """
당신은 특허 분석 전문가입니다. 다음 두 특허의 RAG(Retrieval-Augmented Generation) 
또는 sLLM 관련 청구항을 비교 분석해주세요.

## 원본 특허 (Anchor)
- 특허번호: {anchor_publication_number}
- 청구항: {anchor_claim}

## 인용 특허 (Prior Art)
- 특허번호: {cited_publication_number}
- 청구항: {cited_claim}

## 분석 요청
아래 세 가지 관점에서 분석해주세요:

[유사도 평가]
- 기술적 유사성 점수 (0-100)
- 핵심 공통 기술 요소

[침해 리스크]
- 잠재적 특허 침해 가능성
- 위험 요소 식별

[회피 전략]
- 설계 변경을 통한 회피 방안
- 대안적 기술 접근법
"""
    
    # Output settings
    max_pairs_per_patent: int = 1  # Reduced to save API costs (was 5)
    include_full_context: bool = True  # Include full patent context


# =============================================================================
# Pipeline Configuration
# =============================================================================

@dataclass
class PipelineConfig:
    """Pipeline execution configuration."""
    
    # Concurrency limits (for i5-1340P: 4P + 8E cores)
    max_workers: int = 8  # Limit to prevent UI freezing
    
    # Pre-computation mode
    precompute_embeddings: bool = True
    save_index_to_disk: bool = True


# =============================================================================
# Logging Configuration
# =============================================================================

@dataclass
class LoggingConfig:
    """Logging configuration."""
    
    log_level: str = "INFO"
    log_format: str = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    log_file: Optional[str] = str(PROJECT_ROOT / "logs" / "patent_guard.log")
    
    # Create logs directory
    def __post_init__(self):
        if self.log_file:
            Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)


# =============================================================================
# Master Configuration
# =============================================================================

@dataclass
class PatentGuardConfig:
    """Master configuration aggregating all sub-configs."""
    
    bigquery: BigQueryConfig = field(default_factory=BigQueryConfig)
    domain: DomainConfig = field(default_factory=DomainConfig)
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    faiss: FaissConfig = field(default_factory=FaissConfig)
    painet: PAINETConfig = field(default_factory=PAINETConfig)
    self_rag: SelfRAGConfig = field(default_factory=SelfRAGConfig)
    pipeline: PipelineConfig = field(default_factory=PipelineConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)


# =============================================================================
# Default Configuration Instance
# =============================================================================

config = PatentGuardConfig()


# =============================================================================
# Configuration Helpers
# =============================================================================

def update_config_from_env() -> PatentGuardConfig:
    """Update configuration from environment variables."""
    global config
    
    # BigQuery
    if os.environ.get("GCP_PROJECT_ID"):
        config.bigquery.project_id = os.environ["GCP_PROJECT_ID"]
    
    # OpenAI API
    if os.environ.get("OPENAI_API_KEY"):
        config.embedding.api_key = os.environ["OPENAI_API_KEY"]
        config.self_rag.openai_api_key = os.environ["OPENAI_API_KEY"]
    
    # FAISS paths
    if os.environ.get("FAISS_INDEX_PATH"):
        config.faiss.index_path = Path(os.environ["FAISS_INDEX_PATH"])
    if os.environ.get("FAISS_METADATA_PATH"):
        config.faiss.metadata_path = Path(os.environ["FAISS_METADATA_PATH"])
    
    return config


def print_config_summary() -> None:
    """Print configuration summary."""
    print("\n" + "=" * 70)
    print("🛡️  Patent Guard v2.0 - Configuration Summary (Antigravity Mode)")
    print("=" * 70)
    print(f"\n📊 BigQuery:")
    print(f"   Project: {config.bigquery.project_id}")
    print(f"   Date Range: {config.bigquery.min_filing_date} ~ {config.bigquery.max_filing_date}")
    print(f"   Dry Run: {config.bigquery.dry_run}")
    
    print(f"\n🔍 Domain: {config.domain.domain_name}")
    print(f"   Keywords: {len(config.domain.keywords)} terms")
    print(f"   IPC Codes: {', '.join(config.domain.ipc_codes)}")
    
    print(f"\n🧠 Embedding (OpenAI API):")
    print(f"   Model: {config.embedding.model_id}")
    print(f"   Dimension: {config.embedding.embedding_dim}")
    print(f"   API Key: {'✅ Set' if config.embedding.api_key else '❌ Not set'}")
    
    print(f"\n🗄️  FAISS (In-Memory):")
    print(f"   Index Path: {config.faiss.index_path}")
    print(f"   Index Type: {config.faiss.index_type}")
    
    print(f"\n⚡ Pipeline:")
    print(f"   Max Workers: {config.pipeline.max_workers}")
    print(f"   Pre-compute Mode: {config.pipeline.precompute_embeddings}")
    
    print("=" * 70 + "\n")


if __name__ == "__main__":
    update_config_from_env()
    print_config_summary()
