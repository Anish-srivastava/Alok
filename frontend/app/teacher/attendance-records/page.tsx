"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { 
  ArrowLeft, 
  Calendar, 
  Users, 
  BookOpen, 
  Clock, 
  CheckCircle, 
  XCircle,
  BarChart3,
  Download,
  RefreshCw
} from "lucide-react";

interface AttendanceSession {
  id: string;
  date: string;
  subject: string;
  department: string;
  year: string;
  division: string;
  created_at: string;
  expires_at: string;
  finalized: boolean;
}

interface AttendanceRecord {
  id: string;
  student_id: string;
  student_name: string;
  present: boolean;
  marked_at: string;
}

interface SessionAttendanceData {
  session: AttendanceSession;
  attendance_records: AttendanceRecord[];
  statistics: {
    total_students: number;
    present_count: number;
    absent_count: number;
    attendance_percentage: number;
  };
}

export default function TeacherAttendanceView() {
  const router = useRouter();
  const [sessions, setSessions] = useState<AttendanceSession[]>([]);
  const [selectedSession, setSelectedSession] = useState<AttendanceSession | null>(null);
  const [attendanceData, setAttendanceData] = useState<SessionAttendanceData | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingAttendance, setLoadingAttendance] = useState(false);
  const [error, setError] = useState<string>("");

  // Fetch all sessions (active and completed)
  const fetchSessions = async () => {
    try {
      setLoading(true);
      setError("");
      
      // We'll need to fetch all sessions, not just active ones
      // For now, we'll use the active sessions endpoint but we should create a teacher-specific one
      const response = await fetch("http://localhost:5000/api/attendance/active_sessions");
      const data = await response.json();
      
      if (data.success) {
        setSessions(data.active_sessions);
      } else {
        setError("Failed to fetch sessions");
      }
    } catch (err) {
      console.error("Error fetching sessions:", err);
      setError("Network error occurred");
    } finally {
      setLoading(false);
    }
  };

  // Fetch attendance data for a specific session
  const fetchSessionAttendance = async (sessionId: string) => {
    try {
      setLoadingAttendance(true);
      
      const response = await fetch(`http://localhost:5000/api/attendance/session_attendance/${sessionId}`);
      const data = await response.json();
      
      if (data.success) {
        setAttendanceData(data);
      } else {
        setError("Failed to fetch attendance data");
      }
    } catch (err) {
      console.error("Error fetching attendance:", err);
      setError("Failed to fetch attendance data");
    } finally {
      setLoadingAttendance(false);
    }
  };

  useEffect(() => {
    fetchSessions();
  }, []);

  const handleSessionSelect = (session: AttendanceSession) => {
    setSelectedSession(session);
    fetchSessionAttendance(session.id);
  };

  const exportAttendance = () => {
    if (!attendanceData) return;
    
    const csvContent = [
      ["Student ID", "Student Name", "Status", "Marked At"],
      ...attendanceData.attendance_records.map(record => [
        record.student_id,
        record.student_name,
        record.present ? "Present" : "Absent",
        new Date(record.marked_at).toLocaleString()
      ])
    ].map(row => row.join(",")).join("\\n");
    
    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `attendance_${attendanceData.session.subject}_${attendanceData.session.date}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString();
  };

  const formatTime = (dateStr: string) => {
    return new Date(dateStr).toLocaleTimeString();
  };

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
              <span className="hidden sm:inline">Back to Dashboard</span>
            </button>
            <h1 className="text-xl font-semibold text-gray-800">Attendance Records</h1>
            <button
              onClick={fetchSessions}
              className="flex items-center gap-2 px-3 py-2 bg-blue-50 hover:bg-blue-100 text-blue-600 rounded-lg transition-colors"
            >
              <RefreshCw size={16} />
              <span className="hidden sm:inline">Refresh</span>
            </button>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-6">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Sessions List */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-2xl shadow-lg p-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
                <Calendar className="w-5 h-5 text-blue-600" />
                Sessions
              </h2>
              
              {loading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                  <p className="text-gray-600 mt-2">Loading sessions...</p>
                </div>
              ) : error ? (
                <div className="text-center py-8">
                  <XCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
                  <p className="text-red-600">{error}</p>
                </div>
              ) : sessions.length === 0 ? (
                <div className="text-center py-8">
                  <Calendar className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600">No sessions found</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {sessions.map((session) => (
                    <div
                      key={session.id}
                      onClick={() => handleSessionSelect(session)}
                      className={`p-4 rounded-lg border cursor-pointer transition-all ${
                        selectedSession?.id === session.id
                          ? "border-blue-500 bg-blue-50"
                          : "border-gray-200 hover:border-gray-300 hover:bg-gray-50"
                      }`}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div>
                          <h3 className="font-semibold text-gray-800 flex items-center gap-2">
                            <BookOpen className="w-4 h-4" />
                            {session.subject}
                          </h3>
                          <p className="text-sm text-gray-600">
                            {session.department} - {session.year} - {session.division}
                          </p>
                        </div>
                        <span className={`text-xs font-medium px-2 py-1 rounded ${
                          session.finalized 
                            ? "bg-green-100 text-green-800" 
                            : "bg-yellow-100 text-yellow-800"
                        }`}>
                          {session.finalized ? "Completed" : "Active"}
                        </span>
                      </div>
                      <div className="text-xs text-gray-500">
                        {formatDate(session.date)} at {formatTime(session.created_at)}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Attendance Details */}
          <div className="lg:col-span-2">
            {!selectedSession ? (
              <div className="bg-white rounded-2xl shadow-lg p-8 text-center">
                <Users className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-800 mb-2">Select a Session</h3>
                <p className="text-gray-600">Choose a session from the list to view attendance details</p>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Session Info */}
                <div className="bg-white rounded-2xl shadow-lg p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-xl font-semibold text-gray-800 flex items-center gap-2">
                      <BarChart3 className="w-5 h-5 text-blue-600" />
                      Session Details
                    </h2>
                    {attendanceData && (
                      <button
                        onClick={exportAttendance}
                        className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                      >
                        <Download size={16} />
                        Export CSV
                      </button>
                    )}
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-600">Subject</p>
                      <p className="font-semibold text-gray-800">{selectedSession.subject}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Department</p>
                      <p className="font-semibold text-gray-800">{selectedSession.department}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Class</p>
                      <p className="font-semibold text-gray-800">{selectedSession.year} - {selectedSession.division}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Date</p>
                      <p className="font-semibold text-gray-800">{formatDate(selectedSession.date)}</p>
                    </div>
                  </div>
                </div>

                {/* Statistics */}
                {attendanceData && (
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="bg-white rounded-xl shadow-lg p-4 text-center">
                      <Users className="w-8 h-8 text-blue-600 mx-auto mb-2" />
                      <p className="text-2xl font-bold text-gray-800">{attendanceData.statistics.total_students}</p>
                      <p className="text-sm text-gray-600">Total Students</p>
                    </div>
                    <div className="bg-white rounded-xl shadow-lg p-4 text-center">
                      <CheckCircle className="w-8 h-8 text-green-600 mx-auto mb-2" />
                      <p className="text-2xl font-bold text-green-600">{attendanceData.statistics.present_count}</p>
                      <p className="text-sm text-gray-600">Present</p>
                    </div>
                    <div className="bg-white rounded-xl shadow-lg p-4 text-center">
                      <XCircle className="w-8 h-8 text-red-600 mx-auto mb-2" />
                      <p className="text-2xl font-bold text-red-600">{attendanceData.statistics.absent_count}</p>
                      <p className="text-sm text-gray-600">Absent</p>
                    </div>
                    <div className="bg-white rounded-xl shadow-lg p-4 text-center">
                      <BarChart3 className="w-8 h-8 text-purple-600 mx-auto mb-2" />
                      <p className="text-2xl font-bold text-purple-600">{attendanceData.statistics.attendance_percentage}%</p>
                      <p className="text-sm text-gray-600">Attendance</p>
                    </div>
                  </div>
                )}

                {/* Attendance List */}
                <div className="bg-white rounded-2xl shadow-lg p-6">
                  <h3 className="text-lg font-semibold text-gray-800 mb-4">Attendance Records</h3>
                  
                  {loadingAttendance ? (
                    <div className="text-center py-8">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                      <p className="text-gray-600 mt-2">Loading attendance data...</p>
                    </div>
                  ) : attendanceData ? (
                    <div className="overflow-x-auto">
                      <table className="w-full">
                        <thead>
                          <tr className="border-b border-gray-200">
                            <th className="text-left py-3 px-4 font-semibold text-gray-700">Student ID</th>
                            <th className="text-left py-3 px-4 font-semibold text-gray-700">Name</th>
                            <th className="text-left py-3 px-4 font-semibold text-gray-700">Status</th>
                            <th className="text-left py-3 px-4 font-semibold text-gray-700">Marked At</th>
                          </tr>
                        </thead>
                        <tbody>
                          {attendanceData.attendance_records.map((record) => (
                            <tr key={record.id} className="border-b border-gray-100 hover:bg-gray-50">
                              <td className="py-3 px-4 text-gray-800">{record.student_id}</td>
                              <td className="py-3 px-4 text-gray-800">{record.student_name}</td>
                              <td className="py-3 px-4">
                                <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${
                                  record.present 
                                    ? "bg-green-100 text-green-800" 
                                    : "bg-red-100 text-red-800"
                                }`}>
                                  {record.present ? <CheckCircle size={12} /> : <XCircle size={12} />}
                                  {record.present ? "Present" : "Absent"}
                                </span>
                              </td>
                              <td className="py-3 px-4 text-gray-600 text-sm">
                                {record.marked_at ? new Date(record.marked_at).toLocaleString() : "-"}
                              </td>
                            </tr>
                          ))}
                          {attendanceData.attendance_records.length === 0 && (
                            <tr>
                              <td colSpan={4} className="py-8 text-center text-gray-500">
                                No attendance records found
                              </td>
                            </tr>
                          )}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <p className="text-gray-500">Select a session to view attendance records</p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}