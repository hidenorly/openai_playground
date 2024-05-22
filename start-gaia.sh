#!/bin/bash
source ~/.wasmedge/env
cd ~/gaianet/qdrant
../bin/qdrant &
cd ..
wasmedge --dir .:./dashboard --nn-preload default:GGML:AUTO:Meta-Llama-3-8B-Instruct-Q5_K_M.gguf --nn-preload embedding:GGML:AUTO:all-MiniLM-L6-v2-ggml-model-f16.gguf rag-api-server.wasm --model-name Meta-Llama-3-8B-Instruct-Q5_K_M,all-MiniLM-L6-v2-ggml-model-f16 --ctx-size 8190,384 --prompt-template llama-3-chat --rag-policy system-message --qdrant-collection-name default --qdrant-limit 3 --qdrant-score-threshold 0.5 --web-ui ./ --socket-addr 0.0.0.0:8080 --log-prompts --log-stat --rag-prompt "Use the following pieces of context to answer the user's question.\nIf you don't know the answer, just say that you don't know, don't try to make up an answer.\n----------------\n" --reverse-prompt "<|end|>" &
