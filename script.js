const toggleButton = document.getElementById('toggleButton');
const sendButton = document.getElementById('sendButton');
const transcript = document.getElementById('transcript');

let recognition;
let isRecognizing = false;

toggleButton.addEventListener('click', () => {
    if (!isRecognizing) {
        if ('SpeechRecognition' in window) {
            recognition = new SpeechRecognition();
        } else {
            recognition = new webkitSpeechRecognition();
        }

        recognition.lang = 'en-US';

        recognition.onresult = (event) => {
            const transcriptText = event.results[event.results.length - 1][0].transcript;
            transcript.value += transcriptText;
        };

        recognition.onerror = (event) => {
            console.error('Error occurred:', event.error);
        };

        recognition.onend = () => {
            toggleButton.classList.remove('stop', 'pulse-animation');
            toggleButton.classList.add('start');
            isRecognizing = false;
        };

        recognition.start();
        toggleButton.classList.remove('start');
        toggleButton.classList.add('stop', 'pulse-animation');
        isRecognizing = true;
    } else {
        recognition.stop();
        toggleButton.classList.remove('stop', 'pulse-animation');
        toggleButton.classList.add('start');
        isRecognizing = false;
    }
});

sendButton.addEventListener('click', async () => {
    const recognizedText = transcript.value;

    if (recognizedText !== '') {
        // Send the text to the Flask API
        const response = await fetch('/process-text', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ input_text: recognizedText })
        });

        const data = await response.json();
        
        // Display the response from the API
        alert('Response: ' + data.response_text);

        transcript.value = ''; // Clear the text box after sending
    } else {
        alert('No text to send');
    }
});
