# DSAExplorer 🚀

A comprehensive mobile application for visualizing and exploring Data Structures and Algorithms (DSA). Built with **React Native (Expo)** and a **FastAPI** backend, this app provides interactive visualizers for a wide range of computer science concepts.

## ✨ Features

### 🔍 Searching Algorithms

- Linear Search
- Binary Search

### 📊 Sorting Algorithms

- Bubble Sort
- Selection Sort
- Insertion Sort
- Merge Sort
- Quick Sort

### 🏗️ Data Structures

- **Arrays**: 1D and 2D Array Operations
- **Linked Lists**: Singly, Doubly, Circular Single, and Circular Doubly Linked Lists
- **Basic Structures**: Stack and Queue

### 🌳 Trees & Graphs

- **Tree Traversals**: Inorder, Preorder, and Postorder
- **Graph Traversals**: Breadth-First Search (BFS) and Depth-First Search (DFS)

### 🔐 User Features

- Secure Authentication (JWT-based)
- Algorithm Bookmarking
- Cross-platform support (iOS, Android, Web)

---

## 🛠️ Technology Stack

### Frontend (Mobile App)

- **Framework**: [Expo](https://expo.dev/) (React Native)
- **Language**: TypeScript
- **Styling**: NativeWind (Tailwind CSS for React Native)
- **Navigation**: React Navigation
- **State Management**: React Context API

### Backend (API)

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **Database**: SQLite (SQLAlchemy ORM)
- **Auth**: OAuth2 with JWT (Access & Refresh Tokens)
- **Hosting**: Designed for Render/Docker deployment

---

## 🚀 Getting Started

### Prerequisites

- [Node.js](https://nodejs.org/) (v18+)
- [Python 3.9+](https://www.python.org/)
- [Expo Go](https://expo.dev/expo-go) app (for mobile testing) or an Emulator

### 1. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

The backend will run at `http://127.0.0.1:8000`.

### 2. Frontend Setup

```bash
cd DSAExplorer
npm install
npx expo start
```

- Open **Expo Go** on your phone and scan the QR code.
- Or press `a` for Android Emulator, `i` for iOS Simulator, or `w` for Web.

> [!NOTE]
> Ensure the `API_BASE_URL` in `DSAExplorer/components/Login.tsx` and other components is set to your local IP or the deployed backend URL.

---

## 📁 Project Structure

```text
DSAExplorer/
├── DSAExplorer/            # React Native (Expo) Frontend
│   ├── components/         # UI Components and Visualizers
│   ├── assets/             # Images and Icons
│   ├── App.tsx             # Main Entry Point & Navigation
│   └── tailwind.config.js  # Styling Configuration
├── backend/                # FastAPI Backend
│   ├── main.py             # API Routes and Entry
│   ├── models.py           # Database Models
│   ├── auth.py             # Authentication Logic
│   └── database.py         # SQLAlchemy Setup
└── Image for Report/       # Architectural Diagrams
```

---

## 📐 Architecture Diagrams

You can find architectural diagrams in the `Image for Report` directory:

- **Activity Diagram**: `Activity.drawio.png`
- **Use Case Diagram**: `Case.drawio.png`
- **Sequence Diagram**: `Sequence.drawio.png`

---

## 📄 License

This project is for educational purposes. Feel free to explore and learn!
