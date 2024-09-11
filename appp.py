import os
import base64
import requests
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Render the HTML page
@app.route('/')
def index():
    return render_template('index.html')

# Render the about page
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')

def contact():
    return render_template('contact.html')


@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/service')
def service():
    return render_template('service.html')

from flask import send_from_directory

@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory('static/images', filename)

# Directly set the API key
api_key = "AIzaSyDC-n83rUnoUq6-1qOAMRBoXQ2Dt3c3gBw"  # Replace with your actual key
genai.configure(api_key=api_key)

# Replace with your Plant.id API key
API_KEY = 'CBIhPvZPeyLWjuoVNaW7VS6sbkVmtIsVCFiHiwNgeCCVR3LnGn'



# Create the model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

# API route to process QR data (First API)
@app.route('/process-qr', methods=['POST'])
def process_qr():
    data = request.json  # Get the QR data from the request
    qr_data = data.get('qr_data')  # Extract QR data

    if not qr_data:
        return jsonify({'message': 'No QR data provided'}), 400

    # Create a chat session
    chat_session = model.start_chat(history=[])

    # Send the QR data to the model
    response = chat_session.send_message(qr_data)

    # Return the model's response as JSON
    return jsonify({'message': response.text})
    



# API route to translate the Gemini response (Second API)
@app.route('/translate-response', methods=['POST'])
def translate_response():
    data = request.json
    response_text = data.get('response_text')  # Response from the first API QR scanner 
          # Response from the first API Image Upload 
    selected_language = data.get('language')  # Selected language from the dropdown

    if not response_text or not selected_language:
        return jsonify({'message': 'Invalid data provided'}), 400

    # Prepare translation prompt based on the selected language
    if selected_language == "hindi":
        prompt = f"Translate the following text to Hindi: {response_text}"
    elif selected_language == "gujarati":
        prompt = f"Translate the following text to Gujarati: {response_text}"
    else:
        prompt = f"Arrange this properly {response_text}"  # Default to English, no translation needed

    # Create a chat session for translation
    chat_session = model.start_chat(history=[])
    translation_response = chat_session.send_message(prompt)

    # Return the translated response as JSON
    return jsonify({'translated_message': translation_response.text})


# for image Upload 

# API route to identify plant and translate the result
@app.route('/identify', methods=['POST'])
def identify_plant():
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['image']
    selected_language = request.form.get('language')

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    image_data = base64.b64encode(file.read()).decode('ascii')

    # Call Plant.id API for plant identification
    response = requests.post(
        'https://api.plant.id/v3/identification',
        params={'details': 'url,common_names'},
        headers={'Api-Key': API_KEY},
        json={'images': [image_data]},
    )

    identification = response.json()

    if not identification['result']['is_plant']['binary']:
        return jsonify({'info': 'This is not a plant.'})

    suggestions = identification['result']['classification']['suggestions']
    suggestion = suggestions[0]  # Taking the first suggestion for simplicity

    plant_name = suggestion['name']
    probability = suggestion['probability']
    common_names = suggestion['details'].get('common_names', [])
    plant_details = f"Plant: {plant_name}, Probability: {probability * 100:.2f}%, Common Names: {', '.join(common_names)}"

    # Step 1: Ask for 3 to 4 lines of useful information about the plant
    useful_info_prompt = f"Provide useful information of 2 to 3 line stuctured information line by line   about plant , medicinal property , physical characteristics , treditional usage , releted product   {plant_name}."

    chat_session = model.start_chat(history=[])
    useful_info_response = chat_session.send_message(useful_info_prompt)

    # Step 2: Prepare translation prompt based on the selected language
    combined_info = useful_info_response.text + "\n\n" + plant_details

    if selected_language == "hindi":
        translation_prompt = f"Translate the following text to Hindi: {combined_info}"
    elif selected_language == "gujarati":
        translation_prompt = f"Translate the following text to Gujarati: {combined_info}"
    else:
        translation_prompt = f"Arrange this properly {combined_info}"  # Default to English, no translation needed

    # Step 3: Send the combined info to Gemini API for translation
    translation_response = chat_session.send_message(translation_prompt)

    # Return the translated response as JSON
    return jsonify({
        'translated_message': translation_response.text,
        'original_message': combined_info
    })


# chat bot

# Configure the Gemini API
api_key = "AIzaSyDC-n83rUnoUq6-1qOAMRBoXQ2Dt3c3gBw"  # Replace with your actual key
genai.configure(api_key=api_key)

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

# Flask route to handle speech-to-text input and generate a response
@app.route('/process-text', methods=['POST'])
def process_text():
    data = request.get_json()  # Get the JSON data from the frontend
    input_text = data.get('input_text')  # Extract the text from the request

    # Start a new chat session
    chat_session = model.start_chat(history=[])
    
    # Send the input text to the Gemini model
    response = chat_session.send_message(input_text)
    
    # Return the response as JSON
    return jsonify({'response_text': response.text})

if __name__ == "__main__":
    app.run(debug=True)