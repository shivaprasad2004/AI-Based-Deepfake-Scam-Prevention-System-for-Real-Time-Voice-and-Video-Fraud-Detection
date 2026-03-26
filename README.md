# AI-Based Deepfake Scam Prevention System

An advanced deepfake detection platform designed to identify real-time voice and video fraud. This project provides a robust solution for detecting manipulated media using state-of-the-art machine learning techniques.

---

## 🛠️ Technologies Used

### Backend
- **Flask**: A lightweight Python web framework for the REST API.
- **Flask-SQLAlchemy**: ORM for database management (SQLite).
- **Flask-JWT-Extended**: Secure authentication and session management.
- **OpenCV**: Computer vision for video frame analysis and face extraction.
- **PyTorch**: Deep learning framework for model inference.
- **Librosa**: Audio processing for voice manipulation detection.
- **yt-dlp**: Utility to analyze media directly from URLs (e.g., YouTube).

### Frontend
- **React (Vite)**: Fast and modern frontend development environment.
- **Tailwind CSS**: Utility-first CSS framework for a sleek, responsive UI.
- **Framer Motion**: For smooth animations and interactive components.
- **Chart.js**: Visualizing analysis results and historical data.
- **Axios**: Handling API requests with interceptors for auth.

---

## ✍️ Creator's Notes

This project was built with the vision of creating a user-friendly tool to combat the rising threat of deepfake scams. By combining multi-modal analysis (both audio and video), the system provides a comprehensive "Confidence Score" to help users identify potential fraud. 

Key features include:
- **Real-time Detection**: Fast processing for quick verification.
- **Multi-source Analysis**: Support for local file uploads and direct web links.
- **Detailed Reporting**: Visual breakdowns of detection findings.
- **Secure History**: A private dashboard to manage and review past scans.

---

## 🚀 Getting Started (Cloning the Project)

Follow these steps to set up the project on your local machine.

### Prerequisites
- Python 3.8+
- Node.js 16+
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/shivaprasad2004/AI-Based-Deepfake-Scam-Prevention-System-for-Real-Time-Voice-and-Video-Fraud-Detection.git
cd AI-Based-Deepfake-Scam-Prevention-System-for-Real-Time-Voice-and-Video-Fraud-Detection
```

### 2. Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the backend:
   ```bash
   python app.py
   ```
   *The server will start on http://127.0.0.1:5000*

### 3. Frontend Setup
1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
   *The application will be available at http://localhost:5173 (or 5174)*

---

## 📂 Project Structure
- `/backend`: Flask API, ML models, and detection services.
- `/frontend`: React application and UI components.
- `/backend/uploads`: Temporary storage for analyzed media.

---

## 🛡️ License
Distributed under the MIT License. See `LICENSE` for more information.

---

**Developed with ❤️ by Purnachandar**
