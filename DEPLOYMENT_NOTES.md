# Deployment Notes for Isuku App

## Model Files for Chatbot

The trained chatbot model files are too large to commit to git. For production deployment on Render:

### Option 1: Upload Model Files to Render Disk (Recommended)
1. After deployment, SSH into your Render service
2. Create the directory: `mkdir -p AI_Chatbot/models/isuku_chatbot_llama`
3. Upload the essential model files:
   - `adapter_model.safetensors` (~18MB)
   - `adapter_config.json`
   - `tokenizer.json`
   - `tokenizer_config.json`
   - `special_tokens_map.json`
   - `chat_template.jinja`

### Option 2: Use Cloud Storage
Store model files in AWS S3, Google Cloud Storage, or similar, and download during deployment.

### Option 3: Download from Hugging Face
If you've uploaded the model to Hugging Face, download it during build.

## Essential Model Files
The chatbot service needs these files from `AI_Chatbot/models/isuku_chatbot_llama/`:
- `adapter_model.safetensors` (required)
- `adapter_config.json` (required)
- `tokenizer.json` (required)
- `tokenizer_config.json` (required)
- `special_tokens_map.json` (required)
- `chat_template.jinja` (optional)

## Static Files
Static files are automatically collected during deployment via `collectstatic` command in `render.yaml`.

## Translations
Translation files in `locale/` are included in the repository and will work on production.

## Media Files
User-uploaded images (waste category images, etc.) should be stored in the `media/` directory which is excluded from git but will be available on Render disk.

