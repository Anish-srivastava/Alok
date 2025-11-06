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
  const [demoRecognitionActive, setDemoRecognitionActive] = useState(false);
  const [demoResult, setDemoResult] = useState<RecognizeResult | null>(null);
  const [cameraMode, setCameraMode] = useState<"attendance" | "demo" | "off">("off");
  const [recognitionStatus, setRecognitionStatus] = useState<"idle" | "detecting" | "recognizing" | "success" | "failed">("idle");
  const [recognitionCount, setRecognitionCount] = useState(0);
  const [lastRecognitionTime, setLastRecognitionTime] = useState<Date | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<"checking" | "connected" | "error">("checking");

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

  // Test backend connection
  const testConnection = useCallback(async () => {
    try {
      setConnectionStatus("checking");
      const res = await fetch("http://127.0.0.1:5000/api/demo/recognize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image: "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD" }), // Minimal test image
      });
      
      if (res.ok) {
        setConnectionStatus("connected");
      } else {
        setConnectionStatus("error");
      }
    } catch (error) {
      console.error("Connection test failed:", error);
      setConnectionStatus("error");
    }
  }, []);

  useEffect(() => {
    testConnection();
    const interval = setInterval(testConnection, 30000); // Test every 30 seconds
    return () => clearInterval(interval);
  }, [testConnection]);

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
    if (cameraMode === "attendance" && isLiveActive && selectedSession) {
      await handleMarkAttendance(dataUrl);
    } else if (cameraMode === "demo" && demoRecognitionActive) {
      await handleDemoRecognition(dataUrl);
    }
  }, [cameraMode, isLiveActive, selectedSession, demoRecognitionActive, handleMarkAttendance]);

  const handleDemoRecognition = useCallback(async (dataUrl: string) => {
    if (!demoRecognitionActive) return;

    try {
      setRecognitionStatus("recognizing");
      setRecognitionCount(prev => prev + 1);
      setStatus("🔍 Analyzing face with stored photos...");
      
      const res = await fetch("http://127.0.0.1:5000/api/demo/recognize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image: dataUrl }),
      });
      
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      
      const data = await res.json();
      console.log("Recognition response:", data); // Debug log
      
      if (data.success) {
        if (data.faces && data.faces.length > 0) {
          const face = data.faces[0]; // Get the first detected face
          setDemoResult({
            match: face.match,
            distance: face.distance,
            confidence: face.confidence,
            box: face.box
          });
          
          setLastRecognitionTime(new Date());
          
          if (face.match) {
            setRecognitionStatus("success");
            setStatus(`✅ Face recognized: ${face.match.name} (ID: ${face.match.user_id}) - Confidence: ${face.confidence}% - Distance: ${face.distance?.toFixed(3)}`);
          } else {
            setRecognitionStatus("failed");
            setStatus(`❌ Face not recognized in stored photos - Distance: ${face.distance?.toFixed(3)} - Threshold check failed`);
          }
        } else {
          setRecognitionStatus("detecting");
          setStatus("👤 No face detected in image - Please position your face clearly in the camera");
          setDemoResult(null);
        }
      } else {
        setRecognitionStatus("failed");
        setStatus(`❌ Recognition failed: ${data.error || 'Unknown error'}`);
        setDemoResult(null);
      }
    } catch (err) {
      console.error("Demo recognition error:", err);
      setRecognitionStatus("failed");
      setStatus(`❌ Connection error: ${err instanceof Error ? err.message : 'Network or server error'}`);
      setDemoResult(null);
    }
  }, [demoRecognitionActive]);

  const startAttendance = (session: AttendanceSession) => {
    setSelectedSession(session);
    setCameraMode("attendance");
    setIsLiveActive(true);
    setDemoRecognitionActive(false);
    setStatus(`Ready to mark attendance for ${session.subject}`);
  };

  const stopAttendance = () => {
    setIsLiveActive(false);
    setSelectedSession(null);
    setCameraMode("off");
    setStatus("");
  };

  const startDemoRecognition = () => {
    setDemoRecognitionActive(true);
    setIsLiveActive(false);
    setSelectedSession(null);
    setCameraMode("demo");
    setDemoResult(null);
    setRecognitionStatus("idle");
    setRecognitionCount(0);
    setLastRecognitionTime(null);
    setStatus("📸 Camera ready for face recognition demo - Position your face in front of the camera");
  };

  const stopDemoRecognition = () => {
    setDemoRecognitionActive(false);
    setCameraMode("off");
    setDemoResult(null);
    setRecognitionStatus("idle");
    setStatus("");
  };

  const toggleCamera = () => {
    if (cameraMode === "off") {
      if (selectedSession) {
        startAttendance(selectedSession);
      } else {
        startDemoRecognition();
      }
    } else {
      setCameraMode("off");
      setIsLiveActive(false);
      setDemoRecognitionActive(false);
      setStatus("");
    }
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
        <div className="grid lg:grid-cols-4 gap-6">
          {/* Active Sessions - Left Column */}
          <div className="lg:col-span-1 space-y-6">
            <div className="bg-white rounded-2xl shadow-lg p-6">
              <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                <Clock className="w-5 h-5 text-blue-600" />
                Active Sessions
              </h2>
              
              {loading ? (
                <div className="text-center py-6">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto"></div>
                  <p className="text-gray-600 mt-2 text-sm">Loading...</p>
                </div>
              ) : activeSessions.length === 0 ? (
                <div className="text-center py-6">
                  <Users className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                  <p className="text-gray-600 text-sm">No active sessions</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {activeSessions.map((session) => (
                    <div
                      key={session.session_id}
                      className={`border rounded-lg p-3 transition-all cursor-pointer ${
                        selectedSession?.session_id === session.session_id
                          ? "border-blue-500 bg-blue-50"
                          : "border-gray-200 hover:border-gray-300"
                      }`}
                      onClick={() => cameraMode === "off" && setSelectedSession(session)}
                    >
                      <div className="flex justify-between items-start mb-1">
                        <div>
                          <h3 className="font-medium text-gray-800 text-sm flex items-center gap-1">
                            <BookOpen className="w-3 h-3" />
                            {session.subject}
                          </h3>
                          <p className="text-xs text-gray-600">
                            {session.department} - {session.year}
                          </p>
                        </div>
                        <span className="text-xs font-medium bg-green-100 text-green-800 px-2 py-1 rounded">
                          {getTimeRemaining(session.expires_at)}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Camera Section - Center Column */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white rounded-2xl shadow-lg p-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
                <Camera className="w-5 h-5 text-blue-600" />
                Face Recognition Camera
                {cameraMode !== "off" && (
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    cameraMode === "attendance" ? "bg-blue-100 text-blue-800" : "bg-green-100 text-green-800"
                  }`}>
                    {cameraMode === "attendance" ? "Attendance Mode" : "Demo Mode"}
                  </span>
                )}
              </h2>
              
              {selectedSession && cameraMode === "attendance" && (
                <div className="mb-4 p-3 bg-blue-50 rounded-lg">
                  <p className="text-sm text-blue-800">
                    <strong>Selected:</strong> {selectedSession.subject} - {selectedSession.department}
                  </p>
                </div>
              )}
              
              {cameraMode === "demo" && (
                <div className="mb-4 p-3 bg-green-50 rounded-lg">
                  <p className="text-sm text-green-800">
                    <strong>Demo Mode:</strong> Testing face recognition with stored photos
                  </p>
                </div>
              )}
              
              <div className="relative">
                {cameraMode === "off" ? (
                  <div className="text-center py-12 bg-gray-50 rounded-lg">
                    <Camera className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600 mb-2">Camera Ready</p>
                    <p className="text-sm text-gray-500">
                      {selectedSession ? "Select a session and click start" : "Click start for demo mode"}
                    </p>
                  </div>
                ) : (
                  <CameraCapture
                    onCapture={handleRecognize}
                    isLiveMode={cameraMode === "attendance" || cameraMode === "demo"}
                    captureIntervalMs={cameraMode === "demo" ? 2000 : 3000}
                    facesData={
                      cameraMode === "attendance" && lastResult ? [{
                        box: lastResult.box || [0, 0, 0, 0],
                        match: lastResult.match
                      }] : 
                      cameraMode === "demo" && demoResult ? [{
                        box: demoResult.box || [0, 0, 0, 0],
                        match: demoResult.match
                      }] : []
                    }
                  />
                )}
              </div>
            </div>
          </div>

          {/* Status Sidebar - Right Column */}
          <div className="lg:col-span-1 space-y-6">
            <div className="bg-white rounded-2xl shadow-lg p-6">
              <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-purple-600" />
                Camera Control
                <div className={`w-2 h-2 rounded-full ${
                  connectionStatus === "connected" ? "bg-green-500" :
                  connectionStatus === "error" ? "bg-red-500" :
                  "bg-yellow-500 animate-pulse"
                }`} title={`Backend ${connectionStatus}`}></div>
              </h2>
              
              {/* Unified Camera Button */}
              <button
                onClick={toggleCamera}
                disabled={markingAttendance || (cameraMode === "attendance" && !selectedSession)}
                className={`w-full py-3 px-4 rounded-xl font-medium transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed ${
                  cameraMode === "off" 
                    ? selectedSession
                      ? "bg-blue-600 hover:bg-blue-700 text-white"
                      : "bg-green-600 hover:bg-green-700 text-white"
                    : "bg-red-600 hover:bg-red-700 text-white"
                }`}
              >
                {cameraMode === "off" ? (
                  <>
                    <Play size={18} />
                    {selectedSession ? "Start Attendance" : "Start Demo"}
                  </>
                ) : (
                  <>
                    <Square size={18} />
                    Stop Camera
                  </>
                )}
              </button>

              {/* Mode Selection */}
              {cameraMode === "off" && (
                <div className="mt-4 space-y-2">
                  <button
                    onClick={() => setSelectedSession(null)}
                    className={`w-full py-2 px-3 text-sm rounded-lg transition-colors ${
                      !selectedSession 
                        ? "bg-green-100 text-green-800 border border-green-300"
                        : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                    }`}
                  >
                    Demo Mode
                  </button>
                </div>
              )}

              {/* Status Display */}
              {status && (
                <div className={`mt-4 p-3 rounded-lg border ${
                  recognitionStatus === "success" 
                    ? 'bg-green-50 border-green-200 text-green-800' 
                    : recognitionStatus === "failed"
                    ? 'bg-red-50 border-red-200 text-red-800'
                    : recognitionStatus === "recognizing"
                    ? 'bg-blue-50 border-blue-200 text-blue-800'
                    : 'bg-gray-50 border-gray-200 text-gray-800'
                }`}>
                  <div className="flex items-center gap-2">
                    {recognitionStatus === "recognizing" && (
                      <div className="animate-spin rounded-full h-4 w-4 border-2 border-current border-t-transparent"></div>
                    )}
                    <p className="text-sm font-medium">{status}</p>
                  </div>
                </div>
              )}

              {/* Recognition Statistics */}
              {cameraMode === "demo" && (
                <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                  <h3 className="font-semibold text-gray-800 mb-2 text-sm">Recognition Stats</h3>
                  <div className="space-y-1 text-xs text-gray-600">
                    <p>Attempts: {recognitionCount}</p>
                    <p>Status: <span className={`font-medium ${
                      recognitionStatus === "success" ? "text-green-600" :
                      recognitionStatus === "failed" ? "text-red-600" :
                      recognitionStatus === "recognizing" ? "text-blue-600" :
                      "text-gray-600"
                    }`}>{recognitionStatus.charAt(0).toUpperCase() + recognitionStatus.slice(1)}</span></p>
                    {lastRecognitionTime && (
                      <p>Last: {lastRecognitionTime.toLocaleTimeString()}</p>
                    )}
                  </div>
                </div>
              )}

              {/* Recognition Results */}
              {(cameraMode === "demo" && demoResult) && (
                <div className="mt-4 p-4 bg-white rounded-lg border shadow-sm">
                  <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                    <User className="w-4 h-4" />
                    Recognition Result
                  </h3>
                  {demoResult.match ? (
                    <div className="space-y-3">
                      <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                        <div className="flex items-center gap-2 mb-2">
                          <CheckCircle className="w-5 h-5 text-green-600" />
                          <span className="font-semibold text-green-800">RECOGNIZED</span>
                        </div>
                        <div className="space-y-1">
                          <p className="font-medium text-green-800 text-lg">{demoResult.match.name}</p>
                          <p className="text-sm text-green-700">Student ID: {demoResult.match.user_id}</p>
                          <div className="flex justify-between text-xs text-green-600 mt-2">
                            <span>Confidence: {demoResult.confidence ? demoResult.confidence + '%' : (demoResult.distance ? ((1 - demoResult.distance) * 100).toFixed(1) + '%' : 'N/A')}</span>
                            <span>Distance: {demoResult.distance?.toFixed(3) || 'N/A'}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="p-4 bg-red-50 rounded-lg border border-red-200">
                      <div className="flex items-center gap-2 mb-2">
                        <User className="w-5 h-5 text-red-600" />
                        <span className="font-semibold text-red-800">NOT RECOGNIZED</span>
                      </div>
                      <div className="space-y-1">
                        <p className="text-sm text-red-700">Face detected but not found in database</p>
                        <p className="text-xs text-red-600">
                          Distance: {demoResult.distance?.toFixed(3) || 'N/A'}
                        </p>
                        <p className="text-xs text-red-500 mt-2">
                          Make sure you have registered your photos properly
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Session Info */}
              {selectedSession && (
                <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                  <h3 className="font-semibold text-blue-800 mb-2">Selected Session</h3>
                  <p className="text-sm text-blue-700 font-medium">{selectedSession.subject}</p>
                  <p className="text-xs text-blue-600">
                    {selectedSession.department} - {selectedSession.year} - {selectedSession.division}
                  </p>
                  <p className="text-xs text-blue-600 mt-1">
                    Time left: {getTimeRemaining(selectedSession.expires_at)}
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}