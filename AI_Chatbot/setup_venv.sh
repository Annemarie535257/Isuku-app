#!/bin/bash

# Setup script for AI Chatbot training environment

echo "Setting up virtual environment for AI Chatbot training..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing required packages..."
pip install -r requirements.txt

# Install ipykernel and register it with Jupyter
echo "Setting up Jupyter kernel..."
python -m ipykernel install --user --name=isuku_chatbot --display-name "Python (Isuku Chatbot)"

echo ""
echo "Setup complete!"
echo ""
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To use this environment in Jupyter, select the kernel:"
echo "  'Python (Isuku Chatbot)'"
echo ""

