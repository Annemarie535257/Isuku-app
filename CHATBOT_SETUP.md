# Chatbot Setup Guide

## Overview
The Isuku chatbot is an AI-powered assistant that helps users with waste management questions. It uses a fine-tuned Llama model trained on waste management Q&A data.

## Setup Instructions

### 1. Install Dependencies
The chatbot requires ML/AI packages. Install them in your Django virtual environment:

```bash
# Activate your Django virtual environment
source venv/bin/activate  # or your venv path

# Install required packages
pip install torch transformers peft accelerate
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

### 2. Model Location
The trained model should be located at:
```
AI_Chatbot/models/isuku_chatbot_llama/
```

If the model is in a different location, update the `MODEL_PATH` in `registration/chatbot_service.py`.

### 3. First Load
The first time the chatbot is used, it will load the model (this may take a minute). The model is cached in memory for subsequent requests.

### 4. API Endpoint
The chatbot API is available at:
```
POST /api/chatbot/
```

Request body:
```json
{
    "question": "How do I schedule a waste pickup?"
}
```

Response:
```json
{
    "success": true,
    "response": "You can schedule a waste pickup by..."
}
```

## Usage

### On the Landing Page
1. Visit the landing page
2. Click the chatbot button (💬) in the bottom-right corner
3. Type your question and press Enter or click Send
4. The chatbot will respond with helpful information

### Programmatic Usage
```python
from registration.chatbot_service import generate_response

response = generate_response("How do I sort my waste?")
print(response)
```

## Troubleshooting

### Model Not Found Error
- Ensure the model directory exists at `AI_Chatbot/models/isuku_chatbot_llama/`
- Check that all model files are present (adapter_config.json, adapter_model.bin, etc.)

### Out of Memory Errors
- The model uses CPU/MPS by default (not CUDA)
- For production, consider using a GPU or reducing model size
- The model is loaded once and cached in memory

### Slow Response Times
- First request will be slow (model loading)
- Subsequent requests should be faster
- Consider using a smaller model or GPU acceleration for production

## Model Information
- Base Model: TinyLlama-1.1B-Chat-v1.0
- Fine-tuning: LoRA (Low-Rank Adaptation)
- Training Data: Isuku waste management Q&A dataset
- Languages Supported: English, Kinyarwanda, French

## Notes
- The chatbot is designed for waste management questions
- It may not respond well to unrelated questions
- For production, consider adding rate limiting and caching

