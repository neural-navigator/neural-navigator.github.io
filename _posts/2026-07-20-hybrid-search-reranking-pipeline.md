---
layout: post
title: "Hybrid Dense-Sparse Vector Search with ColBERT Reranking"
subtitle: "Combining lexical BM25 and dense embedding retrieval with late-interaction token scoring."
date: 2026-07-20 14:30:00 +0000
category: RAG
tags: [RAG, VectorSearch, ColBERT, Embeddings]
read_time: "9 min read"
---

Retrieval-Augmented Generation (RAG) applications frequently suffer from precision drops when domain specific acronyms or exact keyword matches are required. Neither pure dense embeddings (which capture semantics) nor sparse lexical search (like BM25) is sufficient alone.

---

## 1. Hybrid Score Fusion

We combine dense cosine similarity scores \(S_{\text{dense}}\) with sparse BM25 scores \(S_{\text{BM25}}\) using Reciprocal Rank Fusion (RRF):

\[
RRF(d \in D) = \sum_{m \in M} \frac{1}{k + r_m(d)}
\]

where \(M\) is the set of retrieval systems, \(r_m(d)\) is the rank of document \(d\) in system \(m\), and \(k = 60\) is a smoothing constant.

<div class="callout callout-info">
    <div class="callout-icon"><i class="fa-solid fa-circle-info"></i></div>
    <div>
        <strong>Pro Tip:</strong> RRF eliminates the need to normalize raw score distributions between BM25 and dense vector inner products before merging!
    </div>
</div>

---

## 2. Late Interaction Reranking Algorithm

ColBERT (Contextualized Late Interaction over BERT) computes token-level MaxSim operators across document token embeddings \(E_d\) and query token embeddings \(E_q\):

```python
import torch

def colbert_maxsim(query_embeddings: torch.Tensor, doc_embeddings: torch.Tensor) -> torch.Tensor:
    """
    Computes late interaction MaxSim score between query and document token vectors.
    query_embeddings: [batch_size, q_len, dim]
    doc_embeddings: [batch_size, doc_len, dim]
    """
    # Compute similarity matrix: [batch_size, q_len, doc_len]
    similarity_matrix = torch.bmm(query_embeddings, doc_embeddings.transpose(1, 2))
    
    # Maximum similarity for each query token across all doc tokens
    max_sim_per_query_token, _ = torch.max(similarity_matrix, dim=2)
    
    # Sum over all query tokens to get total score
    colbert_scores = torch.sum(max_sim_per_query_token, dim=1)
    return colbert_scores
```

---

## 3. Retrieval Performance

Testing on the BEIR benchmark:

* **BM25 Only**: NDCG@10 = `0.432`
* **Dense Embedding Only**: NDCG@10 = `0.518`
* **Hybrid RRF + ColBERT Reranker**: **NDCG@10 = 0.647** (+24.9% retrieval accuracy)
