#!/bin/bash
python3 -m venv venv && source venv/bin/activate && pip install -r ./requirements.txt
echo "############################"
echo "Please be sure to install your openai api key!"
echo "For the terminal windows, resize it to be at least 120 wide and 30 height"

npm install