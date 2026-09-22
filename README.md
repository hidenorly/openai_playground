# openai_playground


## openaicompatible: multi_gpt_client.py

### for apple fm

```
fm serve
```

```
echo "hello" | python3 multi_gpt_client.py -g openaicompatible -e "http://127.0.0.1:1976/v1/chat/completions" -H "Content-Type: application/json"
```

### for ollama

```
echo "hello" | python3 multi_gpt_client.py -g openaicompatible -e "http://localhost:11434/v1/chat/completions" -d default
```




## gpt_compatible-cli.py

```
echo "hello" | python3 gpt_compatible-cli.py -e http://localhost:11434/v1/chat/completions -d default
```