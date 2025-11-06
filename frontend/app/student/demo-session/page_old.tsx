"use client";

import { useState, useCallback, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Camera, ArrowLeft, Play, Square, User, BarChart3, Clock, CheckCircle, BookOpen, Users } from "lucide-react";
import CameraCapture, { FaceData } from "../../components/CameraCapture";

interface RecognizeResult {
  match: { user_id: string; name: string } | null;
  distance: number | null;
  confidence?: number;
  box?: [number, number, number, number];
}

interface AttendanceSession {
  session_id: string;
  date: string;
  subject: string;
  department: string;
  year: string;
  division: string;
  duration_minutes: number;
  expires_at: string;
  created_at: string;
}

interface AttendanceStatus {
  has_marked_attendance: boolean;
  marked_sessions: AttendanceSession[];
}

export default function DemoSession() {
  const router = useRouter();
  const [isLiveActive, setIsLiveActive] = useState(false);
  const [lastResult, setLastResult] = useState<RecognizeResult | null>(null);
  const [processedImage, setProcessedImage] = useState<string | null>(null);
  const [activeSessions, setActiveSessions] = useState<AttendanceSession[]>([]);
  const [attendanceStatus, setAttendanceStatus] = useState<AttendanceStatus | null>(null);
  const [selectedSession, setSelectedSession] = useState<AttendanceSession | null>(null);
  const [attendanceCompleted, setAttendanceCompleted] = useState(false);
  const [loading, setLoading] = useState(true);
  const [studentId, setStudentId] = useState<string>("");
  const [status, setStatus] = useState("");
  const [markingAttendance, setMarkingAttendance] = useState(false);

  // Get student ID from localStorage
  useEffect(() => {
    const storedStudentId = localStorage.getItem("studentId") || localStorage.getItem("username");
    if (storedStudentId) {
      setStudentId(storedStudentId);
    }
  }, []);

  // Fetch active sessions and check attendance status
  const fetchSessionsAndStatus = useCallback(async () => {
    try {
      setLoading(true);
      
      // Fetch active sessions
      const sessionsRes = await fetch("http://localhost:5000/api/attendance/active_sessions");
      const sessionsData = await sessionsRes.json();
      
      if (sessionsData.success) {
        setActiveSessions(sessionsData.active_sessions);
      }

      // Check attendance status for current student
      if (studentId) {
        const statusRes = await fetch(`http://localhost:5000/api/attendance/check_attendance/${studentId}`);
        const statusData = await statusRes.json();
        
        if (statusData.success) {
          setAttendanceStatus(statusData);
          setAttendanceCompleted(statusData.has_marked_attendance);
        }
      }
    } catch (error) {
      console.error("Error fetching sessions and status:", error);
      setStatus("Error loading sessions");
    } finally {
      setLoading(false);
    }
  }, [studentId]);

  useEffect(() => {
    fetchSessionsAndStatus();
    // Refresh every 30 seconds
    const interval = setInterval(fetchSessionsAndStatus, 30000);
    return () => clearInterval(interval);
  }, [fetchSessionsAndStatus]);

  // Calculate time remaining for a session
  const getTimeRemaining = (expiresAt: string) => {
    const now = new Date();
    const expires = new Date(expiresAt);
    const diff = expires.getTime() - now.getTime();
    
    if (diff <= 0) return "Expired";
    
    const minutes = Math.floor(diff / (1000 * 60));
    const seconds = Math.floor((diff % (1000 * 60)) / 1000);
    
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const handleMarkAttendance = useCallback(async (imageDataUrl: string) => {
    if (!selectedSession || markingAttendance) return;

    setMarkingAttendance(true);
    setStatus("Processing attendance...");

    try {
      const res = await fetch("http://127.0.0.1:5000/api/demo/mark_attendance", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          session_id: selectedSession.session_id,
          image: imageDataUrl 
        }),
      });
      const data = await res.json();

      if (data.success) {
        setStatus(`✅ ${data.message}`);
        setAttendanceCompleted(true);
        setSelectedSession(null);
        setIsLiveActive(false);
        // Refresh the sessions and status
        await fetchSessionsAndStatus();
      } else {
        setStatus(`❌ ${data.error}`);
      }
    } catch (err) {
      console.error(err);
      setStatus("❌ Error marking attendance");
    } finally {
      setMarkingAttendance(false);
    }
  }, [selectedSession, markingAttendance, fetchSessionsAndStatus]);

  const handleRecognize = useCallback(async (dataUrl: string) => {
    if (!isLiveActive || !selectedSession) return;
    
    await handleMarkAttendance(dataUrl);
  }, [isLiveActive, selectedSession, handleMarkAttendance]);

  const startAttendance = (session: AttendanceSession) => {
    setSelectedSession(session);
    setIsLiveActive(true);
    setStatus(`Ready to mark attendance for ${session.subject}`);
  };

  const stopAttendance = () => {
    setIsLiveActive(false);
    setSelectedSession(null);
    setStatus("");
  };

  // Show attendance completed state
  if (attendanceCompleted && attendanceStatus?.has_marked_attendance) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50">
        <header className="bg-white/80 backdrop-blur-lg border-b border-slate-200 shadow-sm">
          <div className="px-4 sm:px-6 py-4">
            <div className="flex items-center justify-between">
              <button
                onClick={() => router.back()}
                className="flex items-center gap-2 text-gray-600 hover:text-gray-800 transition-colors"
              >
                <ArrowLeft size={20} />
                <span className="hidden sm:inline">Back</span>
              </button>
              <h1 className="text-xl font-semibold text-gray-800">Attendance Status</h1>
              <div className="w-20" />
            </div>
          </div>
        </header>

        <div className="container mx-auto px-4 py-8">
          <div className="max-w-md mx-auto">
            <div className="bg-white rounded-2xl shadow-xl p-8 text-center">
              <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <CheckCircle className="w-10 h-10 text-green-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-800 mb-4">Attendance Completed!</h2>
              <p className="text-gray-600 mb-6">
                You have successfully marked your attendance for today's sessions.
              </p>
              
              {attendanceStatus?.marked_sessions.map((session) => (
                <div key={session.session_id} className="bg-green-50 rounded-lg p-4 mb-4">
                  <div className="font-semibold text-green-800">{session.subject}</div>
                  <div className="text-sm text-green-600">
                    {session.department} - {session.year} - {session.division}
                  </div>
                </div>
              ))}
              
              <button
                onClick={() => router.push("/student/view-attendance")}
                className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition-colors"
              >
                View Attendance History
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-lg border-b border-slate-200 shadow-sm">
        <div className="px-4 sm:px-6 py-4">
          <div className="flex items-center justify-between">
            <button
              onClick={() => router.back()}
              className="flex items-center gap-2 text-gray-600 hover:text-gray-800 transition-colors"
            >
              <ArrowLeft size={20} />
              <span className="hidden sm:inline">Back</span>
            </button>
            <h1 className="text-xl font-semibold text-gray-800">Mark Attendance</h1>
            <div className="w-20" />
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-6">
        <div className="grid lg:grid-cols-2 gap-8">
          {/* Active Sessions */}
          <div className="space-y-6">
            <div className="bg-white rounded-2xl shadow-lg p-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
                <Clock className="w-5 h-5 text-blue-600" />
                Active Sessions
              </h2>
              
              {loading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                  <p className="text-gray-600 mt-2">Loading sessions...</p>
                </div>
              ) : activeSessions.length === 0 ? (
                <div className="text-center py-8">
                  <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600">No active attendance sessions</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {activeSessions.map((session) => (
                    <div
                      key={session.session_id}
                      className={`border rounded-lg p-4 transition-all cursor-pointer ${
                        selectedSession?.session_id === session.session_id
                          ? "border-blue-500 bg-blue-50"
                          : "border-gray-200 hover:border-gray-300"
                      }`}
                      onClick={() => !isLiveActive && startAttendance(session)}
                    >
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <h3 className="font-semibold text-gray-800 flex items-center gap-2">
                            <BookOpen className="w-4 h-4" />
                            {session.subject}
                          </h3>
                          <p className="text-sm text-gray-600">
                            {session.department} - {session.year} - {session.division}
                          </p>
                        </div>
                        <span className="text-xs font-medium bg-green-100 text-green-800 px-2 py-1 rounded">
                          {getTimeRemaining(session.expires_at)} left
                        </span>
                      </div>
                      <div className="text-xs text-gray-500">
                        Created: {new Date(session.created_at).toLocaleTimeString()}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Camera Section */}
          <div className="space-y-6">
            <div className="bg-white rounded-2xl shadow-lg p-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
                <Camera className="w-5 h-5 text-blue-600" />
                Face Recognition
              </h2>
              
              {!selectedSession ? (
                <div className="text-center py-8">
                  <Camera className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600">Select a session to start marking attendance</p>
                </div>
              ) : (
                <>
                  <div className="mb-4 p-3 bg-blue-50 rounded-lg">
                    <p className="text-sm text-blue-800">
                      <strong>Selected:</strong> {selectedSession.subject} - {selectedSession.department}
                    </p>
                  </div>
                  
                  <div className="relative">
                    <CameraCapture
                      onCapture={handleRecognize}
                      isActive={isLiveActive}
                      overlayData={lastResult ? [{ 
                        box: lastResult.box || [0, 0, 0, 0], 
                        match: lastResult.match 
                      }] : []}
                    />
                    
                    <div className="mt-4 flex gap-3">
                      {!isLiveActive ? (
                        <button
                          onClick={() => setIsLiveActive(true)}
                          disabled={markingAttendance}
                          className="flex-1 bg-blue-600 text-white py-3 px-4 rounded-xl hover:bg-blue-700 transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
                        >
                          <Play size={18} />
                          Start Camera
                        </button>
                      ) : (
                        <button
                          onClick={stopAttendance}
                          disabled={markingAttendance}
                          className="flex-1 bg-red-600 text-white py-3 px-4 rounded-xl hover:bg-red-700 transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
                        >
                          <Square size={18} />
                          Stop Camera
                        </button>
                      )}
                    </div>
                  </div>
                </>
              )}
              
              {status && (
                <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-700">{status}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
            {/* Left Section */}
            <div className="flex items-center gap-4">
              <button
                onClick={() => router.push("/dashboard")}
                className="p-2 rounded-lg bg-slate-100 hover:bg-slate-200 transition-colors group"
              >
                <ArrowLeft className="w-6 h-6 text-slate-600 group-hover:text-slate-800 transition-colors" />
              </button>
              
              <div className="flex items-center gap-3">
                <div className="p-3 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl shadow-lg">
                  <Camera className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-xl sm:text-2xl font-bold text-slate-800 tracking-tight">Face Recognition Demo</h1>
                  <p className="text-slate-600 text-sm font-medium">Live demonstration and testing</p>
                </div>
              </div>
            </div>

            {/* Status Indicator */}
            <div className="flex items-center gap-3">
              <div className={`flex items-center gap-2 px-4 py-2 rounded-xl border-2 transition-all ${
                isLiveActive 
                  ? "bg-emerald-50 border-emerald-200 shadow-sm" 
                  : "bg-slate-100 border-slate-200"
              }`}>
                <div className={`w-2 h-2 rounded-full ${
                  isLiveActive ? "bg-emerald-500 animate-pulse" : "bg-slate-400"
                }`} />
                <span className={`text-sm font-semibold ${
                  isLiveActive ? "text-emerald-700" : "text-slate-600"
                }`}>
                  {isLiveActive ? "LIVE" : "STANDBY"}
                </span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Controls - Moved Above */}
      <div className="px-4 sm:px-6 py-4 bg-white/50 border-b border-slate-200">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
            {/* Left Controls */}
            <div className="flex flex-wrap gap-3">
              <button
                onClick={() => setIsLiveActive(!isLiveActive)}
                className={`px-6 py-3 rounded-xl font-semibold transition-all duration-300 flex items-center justify-center gap-3 border-2 ${
                  isLiveActive 
                    ? "bg-red-50 hover:bg-red-100 text-red-600 border-red-200 hover:border-red-300 shadow-sm" 
                    : "bg-emerald-50 hover:bg-emerald-100 text-emerald-600 border-emerald-200 hover:border-emerald-300 shadow-sm"
                }`}
              >
                {isLiveActive ? (
                  <>
                    <Square className="w-5 h-5" />
                    Stop Demo
                  </>
                ) : (
                  <>
                    <Play className="w-5 h-5" />
                    Start Demo
                  </>
                )}
              </button>

              <button
                onClick={() => router.push("/dashboard")}
                className="px-6 py-3 rounded-xl font-semibold bg-blue-50 hover:bg-blue-100 text-blue-600 border-2 border-blue-200 hover:border-blue-300 transition-all duration-300 flex items-center justify-center gap-3 shadow-sm"
              >
                <ArrowLeft className="w-5 h-5" />
                Back to Dashboard
              </button>
            </div>

            {/* Right Stats */}
            <div className="flex flex-wrap gap-4 text-sm">
              <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white border border-slate-200 shadow-sm">
                <span className="text-slate-600 font-medium">Status:</span>
                <span className={`font-semibold ${
                  isLiveActive ? "text-emerald-600" : "text-amber-600"
                }`}>
                  {isLiveActive ? "Active" : "Inactive"}
                </span>
              </div>
              
              <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white border border-slate-200 shadow-sm">
                <span className="text-slate-600 font-medium">Last Result:</span>
                <span className={`font-semibold ${
                  lastResult?.match ? "text-emerald-600" : "text-slate-600"
                }`}>
                  {lastResult?.match ? "Match Found" : "No Match"}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="p-4 sm:p-6">
        <div className="max-w-7xl mx-auto">
          {/* Camera and Results Section */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 sm:gap-8 mb-8">
            {/* Camera Feed */}
            <div className="bg-white rounded-2xl border-2 border-purple-200 p-6 shadow-lg">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-3 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl shadow-lg">
                  <Camera className="w-5 h-5 text-white" />
                </div>
                <h2 className="text-xl font-bold text-slate-800">Camera Feed</h2>
              </div>
              
              <div className="relative rounded-xl overflow-hidden bg-slate-100 border-2 border-slate-200">
                <CameraCapture
                  isLiveMode={isLiveActive}
                  captureIntervalMs={1000}
                  onCapture={handleRecognize}
                  facesData={
                    lastResult && lastResult.box
                      ? [{
                          ...lastResult,
                          box: lastResult.box
                        }]
                      : []
                  }
                />
                
                {/* Overlay Status */}
                {!isLiveActive && (
                  <div className="absolute inset-0 bg-slate-900/70 flex items-center justify-center backdrop-blur-sm">
                    <div className="text-center">
                      <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center mx-auto mb-4 shadow-lg">
                        <Play className="w-8 h-8 text-slate-600" />
                      </div>
                      <p className="text-white font-semibold">Click Start Demo to begin</p>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Results Panel */}
            <div className="bg-white rounded-2xl border-2 border-blue-200 p-6 shadow-lg">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-3 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl shadow-lg">
                  <BarChart3 className="w-5 h-5 text-white" />
                </div>
                <h2 className="text-xl font-bold text-slate-800">Recognition Results</h2>
              </div>

              {/* Results Content */}
              <div className="space-y-6">
                {/* Status Card */}
                <div className={`p-4 rounded-xl border-2 transition-all ${
                  lastResult?.match 
                    ? "bg-emerald-50 border-emerald-200 shadow-sm" 
                    : "bg-slate-50 border-slate-200"
                }`}>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-slate-600 text-sm font-medium">Status</span>
                    <div className={`px-3 py-1 rounded-full text-xs font-semibold ${
                      lastResult?.match 
                        ? "bg-emerald-100 text-emerald-700 border border-emerald-200" 
                        : "bg-slate-100 text-slate-600 border border-slate-200"
                    }`}>
                      {lastResult?.match ? "MATCH FOUND" : "NO MATCH"}
                    </div>
                  </div>
                  <p className="text-slate-800 font-bold">
                    {lastResult?.match 
                      ? `Identified: ${lastResult.match.name}` 
                      : "No face recognized"}
                  </p>
                </div>

                {/* User Info - Only shown when match is found */}
                {lastResult?.match && (
                  <div className="p-4 rounded-xl bg-blue-50 border-2 border-blue-200 shadow-sm">
                    <div className="flex items-center gap-3 mb-3">
                      <div className="p-2 bg-blue-500 rounded-lg">
                        <User className="w-5 h-5 text-white" />
                      </div>
                      <h3 className="text-lg font-bold text-slate-800">User Information</h3>
                    </div>
                    <div className="space-y-3">
                      <div>
                        <span className="text-slate-600 text-sm font-medium">Name:</span>
                        <p className="text-slate-800 font-semibold">{lastResult.match.name}</p>
                      </div>
                      <div>
                        <span className="text-slate-600 text-sm font-medium">User ID:</span>
                        <p className="text-slate-800 font-mono text-sm bg-slate-100 px-2 py-1 rounded">{lastResult.match.user_id}</p>
                      </div>
                    </div>
                  </div>
                )}

                {/* No Match State */}
                {!lastResult?.match && isLiveActive && (
                  <div className="p-6 rounded-xl bg-slate-50 border-2 border-slate-200">
                    <div className="text-center">
                      <div className="w-12 h-12 bg-slate-200 rounded-full flex items-center justify-center mx-auto mb-3">
                        <User className="w-6 h-6 text-slate-500" />
                      </div>
                      <p className="text-slate-700 font-semibold">No face recognized</p>
                      <p className="text-slate-500 text-sm mt-1">Ensure face is clearly visible in camera</p>
                    </div>
                  </div>
                )}

                {/* Instructions */}
                <div className="p-4 rounded-xl bg-gradient-to-br from-slate-50 to-blue-50 border-2 border-slate-200">
                  <h4 className="text-slate-800 font-bold mb-3">How it works:</h4>
                  <ul className="text-slate-600 text-sm space-y-2">
                    <li className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 bg-blue-500 rounded-full"></span>
                      Click "Start Demo" to begin face recognition
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 bg-blue-500 rounded-full"></span>
                      Position your face clearly in the camera view
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 bg-blue-500 rounded-full"></span>
                      Results will appear here in real-time
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 bg-blue-500 rounded-full"></span>
                      Click "Stop Demo" to end the session
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          {/* Processed Image Section */}
          {processedImage && (
            <div className="bg-white rounded-2xl border-2 border-cyan-200 p-6 shadow-lg">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-3 bg-gradient-to-br from-cyan-500 to-cyan-600 rounded-xl shadow-lg">
                  <Camera className="w-5 h-5 text-white" />
                </div>
                <h3 className="text-xl font-bold text-slate-800">Processed Image</h3>
              </div>
              
              <div className="flex justify-center">
                <div className="rounded-xl overflow-hidden bg-slate-100 border-2 border-slate-200 max-w-2xl shadow-lg">
                  <img 
                    src={processedImage} 
                    alt="Processed" 
                    className="w-full h-auto max-h-96 object-contain"
                  />
                </div>
              </div>
              
              <p className="text-slate-600 text-sm mt-4 text-center">
                AI-processed image with face detection and recognition overlay
              </p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}