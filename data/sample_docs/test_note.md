# Transformer Architecture

Transformers were introduced in the 2017 paper "Attention is All You Need" by Vaswani et al.
The key innovation was replacing recurrent layers with self-attention mechanisms.

## Self-Attention

Self-attention allows the model to weigh the importance of different words in a sentence
relative to each other. For each word, it computes a query, key, and value vector.
The attention score is computed as the dot product of the query with all keys,
scaled by the square root of the dimension.

## Why Transformers Matter

Before transformers, NLP relied on RNNs and LSTMs which processed tokens sequentially.
This made parallelization difficult and caused vanishing gradient problems on long sequences.
Transformers process all tokens simultaneously, making them much faster to train.

## Key Components

- Multi-head attention: runs attention multiple times in parallel
- Positional encoding: injects position information since attention is order-agnostic
- Feed-forward layers: applied to each position independently
- Layer normalization: stabilizes training
EOF