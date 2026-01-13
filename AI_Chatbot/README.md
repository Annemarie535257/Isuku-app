# Isuku Chatbot - Llama Model Training

This directory contains the training notebook and dataset for the Isuku waste management chatbot.

## Setup

### 1. Create and Activate Virtual Environment

**On macOS/Linux:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

**On Windows:**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate
```

### 2. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt
```

### 3. Setup Jupyter Kernel (Optional but Recommended)

To use this virtual environment in Jupyter notebooks:

```bash
# Make sure venv is activated first
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

# Install and register the kernel
python -m ipykernel install --user --name=isuku_chatbot --display-name "Python (Isuku Chatbot)"
```

Then in your Jupyter notebook, select the kernel: **"Python (Isuku Chatbot)"**

### 4. Quick Setup (Using Script)

Alternatively, you can use the setup script:

```bash
chmod +x setup_venv.sh
./setup_venv.sh
```

## Running the Notebook

1. Activate the virtual environment:
   ```bash
   source venv/bin/activate  # macOS/Linux
   # or
   venv\Scripts\activate  # Windows
   ```

2. Start Jupyter:
   ```bash
   jupyter notebook
   ```

3. Open `train_llama_chatbot.ipynb`

4. Select the kernel: **"Python (Isuku Chatbot)"** (if you set it up) or use the default Python kernel

5. Run all cells to train the model

## Model Output

After training, the model will be saved in:
- `./models/isuku_chatbot_llama/` - Final trained model
- `./models/isuku_chatbot_llama/checkpoints/` - Training checkpoints

## Requirements

- Python 3.8 or higher
- CUDA-capable GPU (recommended for faster training)
- At least 8GB RAM (16GB+ recommended)
- 10GB+ free disk space for model files

## Notes

- The notebook uses TinyLlama by default for faster training. You can change the model in the notebook.
- For larger models like Llama-2, you may need Hugging Face authentication token.
- Training time depends on your hardware and dataset size.

