# Face Recognition Attendance System

A full-stack attendance management system using facial recognition technology.

## Tech Stack

- **Frontend**: Next.js 15, React 19, TailwindCSS
- **Backend**: Flask, Python 3.11
- **Database**: Supabase (PostgreSQL)
- **Face Recognition**: DeepFace, MTCNN
- **Deployment**: Render

## Features

- 🔐 User Authentication (Student/Teacher roles)
- 📸 Face Recognition for Attendance
- 📊 Attendance Records & Analytics
- 👤 Student Registration & Management
- 🎯 Real-time Attendance Tracking
- 📱 Responsive Design

## Local Development

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file with your credentials:
```bash
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
THRESHOLD=0.6
```

4. Run the server:
```bash
python app.py
```

Backend will run on `http://localhost:5000`

### Frontend Setup

1. Navigate to frontend directory:
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

Frontend will run on `http://localhost:3000`

## Deployment on Render

### Prerequisites
- GitHub account
- Render account ([render.com](https://render.com))
- Supabase account with database setup

### Steps to Deploy

1. **Push code to GitHub**:
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

2. **Create New Web Service on Render**:
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect `render.yaml`

3. **Set Environment Variables** (in Render Dashboard):
   
   **For Backend Service**:
   - `SUPABASE_URL` - Your Supabase project URL
   - `SUPABASE_KEY` - Your Supabase anon/public key
   - `THRESHOLD` - Face recognition threshold (default: 0.6)

4. **Deploy**:
   - Render will automatically build and deploy both services
   - Backend URL: `https://attendance-backend.onrender.com`
   - Frontend URL: `https://attendance-frontend.onrender.com`

### Important Notes

- **Free Tier**: Render free tier services spin down after inactivity. First request may take 50+ seconds.
- **Environment Variables**: Make sure to add all required env vars in Render dashboard.
- **Build Time**: Initial build may take 5-10 minutes due to ML model downloads.
- **Update Frontend API URL**: Update the backend API URL in frontend code after deployment.

## Project Structure

```
├── backend/
│   ├── app.py              # Main Flask application
│   ├── requirements.txt    # Python dependencies
│   ├── build.sh           # Build script for Render
│   ├── .env.example       # Environment variables template
│   ├── auth/              # Authentication routes
│   ├── student/           # Student-related routes
│   └── teacher/           # Teacher-related routes
├── frontend/
│   ├── app/               # Next.js app directory
│   ├── public/            # Static assets
│   ├── package.json       # Node dependencies
│   └── next.config.ts     # Next.js configuration
├── render.yaml            # Render deployment configuration
└── README.md             # This file
```

## Environment Variables

### Backend (.env)
```bash
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
THRESHOLD=0.6
```

### Frontend (if needed)
```bash
NEXT_PUBLIC_API_URL=http://localhost:5000
```

## API Endpoints

### Authentication
- `POST /api/signup` - User registration
- `POST /api/signin` - User login
- `POST /api/logout` - User logout

### Student
- `POST /api/register-student` - Register student with face data
- `GET /api/students` - Get all students
- `POST /api/demo/recognize` - Face recognition demo

### Attendance
- `POST /api/attendance/create_session` - Create attendance session
- `GET /api/attendance` - Get attendance records
- `POST /api/attendance/mark_attendance` - Mark attendance

## License

MIT License

## Support

For issues and questions, please create an issue in the GitHub repository.
