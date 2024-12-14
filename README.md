# Ringsewa - Real-Time Communication and Audio Transcription System

## Introduction
**Ringsewa** is a web platform that allows users to communicate in real time through audio (or video) calls, powered by **WebRTC** technology. In addition, it transcribes the audio during calls to provide useful insights such as product details (name, description, price, location) using advanced AI techniques like **OpenAI’s Whisper** for transcription and **NER (Named Entity Recognition)** for extracting relevant data.

## Key Features
1. **Real-Time Communication**: Users can make audio or video calls with each other directly through the browser using WebRTC, which means there’s no need for additional plugins or software installations.
2. **Audio Transcription**: Any audio recorded during calls is automatically transcribed into text using **Whisper**, a powerful speech-to-text model from OpenAI.
3. **Data Extraction**: The transcribed text is analyzed for product details using **NER** (Named Entity Recognition), helping the system to identify and extract important information such as product names, prices, descriptions, and locations.
4. **Backend Management**: All transcriptions and extracted data are saved in a **Django** backend that manages users and products efficiently.

## How It Works
1. **WebRTC Communication**: When two users connect on the platform, they can initiate a real-time audio or video call. WebRTC ensures that this happens without requiring any downloads or plugins.
2. **Recording the Call**: The audio from the call is recorded and stored in the backend.
3. **Transcription Process**: Once the audio is recorded, it is sent to OpenAI’s Whisper API, which transcribes the Nepali audio into text.
4. **Data Extraction**: The transcribed text is processed by another OpenAI API (GPT-3) to extract useful information like product name, description, price, and location.
5. **Database Update**: The extracted data is saved in the backend (Django) and linked to the relevant product.

## Project Structure
- **Django Backend**: The backend is built using Django. It handles user management, WebRTC signaling, and saving transcriptions to the database.
- **WebRTC (Frontend)**: The frontend handles the real-time audio/video communication. It is built using simple HTML, CSS, and JavaScript to enable WebRTC functionality.
- **AI Services**: Uses OpenAI's APIs to transcribe audio and extract data from transcriptions.

## Technologies Used
- **WebRTC**: For peer-to-peer communication (audio/video calls).
- **Django**: For backend services such as user management and product data storage.
- **OpenAI Whisper**: For converting audio into text.
- **OpenAI GPT-3**: For extracting product details from the transcribed text.
- **JavaScript**: For managing WebRTC frontend interactions.

## Getting Started

### Prerequisites
Before setting up the project, make sure you have the following installed:
1. **Python 3.8+**
2. **Node.js and npm** (for frontend dependencies)
3. **Django** (for backend development)
4. **WebRTC** (for real-time communication)
5. **A working OpenAI API key** (for transcription and NER features)

### Step 1: Clone the Repository
Clone the project repository to your local machine using Git:
```bash
git clone https://github.com/yourusername/ringsewa.git
cd ringsewa
```

### Step 2: Set Up Backend (Django)
1. **Create a Virtual Environment**:
   It’s recommended to use a virtual environment to avoid dependency conflicts. Run the following commands:
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # On Windows use venv\Scripts\activate
   ```

2. **Install Python Dependencies**:
   Inside your virtual environment, install the required Python packages by running:
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Configure Django Settings**:
   - Update the `settings.py` file in the backend with your **OpenAI API Key**, **BASE_MEDIA_URL**, and database settings.
   - You can store your sensitive information like API keys in `.env` and use `django-environ` to load them into your settings.

4. **Migrate the Database**:
   Run the following commands to create the necessary database tables:
   ```bash
   cd backend
   python manage.py migrate
   ```

5. **Create a Superuser (Optional)**:
   If you want to access the Django admin panel, create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

6. **Start the Django Development Server**:
   Run the backend server with:
   ```bash
   python manage.py runserver
   ```

   The Django server will run on `http://localhost:8000`.

### Step 3: Set Up Frontend (WebRTC)
1. **Navigate to the Frontend Directory**:
   ```bash
   cd ear
   ```

2. **Install Frontend Dependencies**:
   You’ll need **npm** (Node Package Manager) to install the required dependencies for the WebRTC frontend. Run:
   ```bash
   npm install
   ```

3. **Start the Frontend Development Server**:
   Run the following command to start the frontend:
   ```bash
   npm start
   ```

   This will start the frontend server, typically accessible at `http://localhost:3000`.

### Step 4: Testing the Application
1. **Access the Platform**:
   Open your browser and visit `http://localhost:3000` (for frontend) and `http://localhost:8000` (for backend). 
   You should be able to make audio or video calls directly through your browser.

2. **Make a Call**:
   Once the users are connected, the system will automatically start transcribing the conversation and extracting the relevant data.

### Step 5: Additional Configuration
- You may need to configure your WebRTC signaling server for production.
- Set up proper SSL/TLS certificates if deploying to production (important for WebRTC).
- Ensure that the OpenAI API key is correctly set in both the backend and frontend.

## Use Cases
- **Customer Service**: Can be used by customer service representatives to handle product inquiries. The system automatically transcribes the conversation and extracts important product details.
- **Remote Collaboration**: Ideal for teams working remotely who need to discuss products or services, with automatic transcription and data extraction to save time.
- **E-commerce**: Sellers can use the platform to discuss products with buyers, and the system can automatically extract the product details from the conversation, helping in record-keeping.

## Conclusion
**Ringsewa** is an innovative platform that combines real-time communication with powerful AI tools to improve workflows and assist users in managing conversations. Whether for business, e-commerce, or collaboration, it provides an easy-to-use, efficient solution to manage audio data and insights.

