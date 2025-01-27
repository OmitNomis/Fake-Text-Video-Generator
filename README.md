# Fake Text Story Video Generator

## Sample Video

<video src='[https://raw.github.com/OmitNomis/Light-Version---Fake-Text-Story-Generator.git](https://github.com/OmitNomis/Light-Version---Fake-Text-Story-Generator/blob/main/sample-video/output_video%20.mp4)' width=180/>


Welcome to the Fake Text Story Video Generator! This application allows you to create engaging text message videos with realistic conversations.

## Features

- Create messages for both sender and receiver
- Edit messages freely at any time
- Add fun sound effects to individual messages
- Choose from various voice actors for both participants
- Select your preferred background video style

## Requirements

- Python 3.7+
- Flask
- Flask-CORS
- MoviePy
- gTTS
- Selenium
- Requests
- PIL (Pillow)

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/Fake-Text-Story-Video-Generator.git
    cd Fake-Text-Story-Video-Generator
    ```

2. Create a virtual environment and activate it:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

4. Download and install the ChromeDriver for Selenium:
    - [ChromeDriver Download](https://sites.google.com/a/chromium.org/chromedriver/downloads)
    - Make sure the ChromeDriver version matches your installed Chrome browser version.

5. Place the ChromeDriver executable in a directory included in your system's PATH.

## Running the App

1. Start the Flask application:
    ```sh
    python app.py
    ```

2. Open your web browser and navigate to `http://127.0.0.1:5001`.

## Usage

1. Enter your ElevenLabs API key to enable voice features.
2. Type your messages in the input box and press Enter or click Send.
3. Click on any message to edit, add sound effects, or manage message options.
4. Click on the profile image to upload your own profile image. Click on the header name to edit your name.
5. Select voice actors for both sender and receiver.
6. Choose your preferred background video style.
7. Click "Generate Video" to create your text message video.
