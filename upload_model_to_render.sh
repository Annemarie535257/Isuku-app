#!/bin/bash
# Script to upload model files to Render
# Usage: ./upload_model_to_render.sh <render-service-name>

SERVICE_NAME=${1:-"isuku-app"}
MODEL_DIR="AI_Chatbot/models/isuku_chatbot_llama"

echo "This script helps you upload model files to Render."
echo ""
echo "Option 1: Use Render Shell (Recommended)"
echo "1. Go to your Render dashboard"
echo "2. Open Shell for service: $SERVICE_NAME"
echo "3. Run these commands:"
echo ""
echo "   mkdir -p $MODEL_DIR"
echo "   # Then use 'scp' or Render's file upload feature"
echo ""
echo "Option 2: Use SCP (if you have SSH access)"
echo "   scp -r $MODEL_DIR/*.safetensors $MODEL_DIR/*.json $MODEL_DIR/*.jinja user@render:/opt/render/project/src/$MODEL_DIR/"
echo ""
echo "Essential files to upload:"
echo "  - adapter_model.safetensors"
echo "  - adapter_config.json"
echo "  - tokenizer.json"
echo "  - tokenizer_config.json"
echo "  - special_tokens_map.json"
echo "  - chat_template.jinja (if exists)"
echo ""
echo "After uploading, restart your Render service."

