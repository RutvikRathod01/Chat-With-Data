# Chat with your data
This is an AI tool to perform question answering on your uploaded document(doc, excel, pdf)

# How to run?
### STEPS:

Clone the repository

```bash
https://github.com/Tokir-Vora/chat-with-your-data.git
cd chat-with-your-data
```
### STEP 01- Create a virtual environment after opening the repository

```bash
python -m venv venv
source venv/bin/activate
```

### STEP 02- install the requirements

```bash
pip install -r requirements.txt
```

### STEP 03- create .env file

```bash
GROQ_API_KEY = < Provide your Groq api token >
NGROK_AUTH_TOKEN = < Provide your ngrok auth token >
```

### STEP 04- Run Gradio app
```bash
# Finally run the following command
cd src
python main.py
```

## Note : Generate flake8 report using below command
```bash
# Change the directory to the location where this file exists.
./generate_flake8_reports.sh
```