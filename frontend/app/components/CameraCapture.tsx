"use client";

import React, { useRef, useEffect, useState } from "react";

export interface FaceData {
  box: [number, number, number, number];
  match: { user_id: string; name: string } | null;
  confidence?: number;
}

interface CameraCaptureProps {
  onCapture: (dataUrl: string) => void;
  captureIntervalMs?: number | null;
  singleShot?: boolean;
  isLiveMode?: boolean;
  facesData?: FaceData[];
}

const CameraCapture: React.FC<CameraCaptureProps> = ({
  onCapture,
  captureIntervalMs = null,
  singleShot = false,
  isLiveMode = false,
  facesData = [],
}) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const [cameraStatus, setCameraStatus] = useState<"loading" | "active" | "stopped">("stopped");
  const [cameraError, setCameraError] = useState<string>("");

  const startCamera = async () => {
    try {
      setCameraStatus("loading");
      setCameraError("");
      
      // Check if getUserMedia is available
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error("Camera access not supported in this browser");
      }

      // Try to get camera permission with fallback constraints
      let stream;
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          video: { 
            width: { ideal: 640 }, 
            height: { ideal: 480 }, 
            facingMode: "user" 
          },
        });
      } catch (err) {
        // Fallback to basic video constraints
        console.warn("Failed with ideal constraints, trying basic constraints:", err);
        stream = await navigator.mediaDevices.getUserMedia({
          video: true
        });
      }

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        // Wait for video to be ready
        videoRef.current.onloadedmetadata = () => {
          setCameraStatus("active");
        };
      }
    } catch (err: any) {
      console.error("Camera error:", err);
      
      let errorMessage = "Failed to access camera. ";
      
      if (err.name === "NotAllowedError" || err.name === "PermissionDeniedError") {
        errorMessage += "Please allow camera permissions in your browser.";
      } else if (err.name === "NotFoundError" || err.name === "DevicesNotFoundError") {
        errorMessage += "No camera device found.";
      } else if (err.name === "NotReadableError" || err.name === "TrackStartError") {
        errorMessage += "Camera is already in use by another application.";
      } else if (err.name === "OverconstrainedError" || err.name === "ConstraintNotSatisfiedError") {
        errorMessage += "Camera constraints not supported.";
      } else if (err.name === "NotSupportedError") {
        errorMessage += "Camera access not supported in this browser.";
      } else if (err.name === "SecurityError") {
        errorMessage += "Camera access blocked due to security settings. Try using HTTPS.";
      } else {
        errorMessage += `Error: ${err.message || err.name || "Unknown error"}`;
      }
      
      setCameraError(errorMessage);
      setCameraStatus("stopped");
    }
  };

  const stopCamera = () => {
    const stream = videoRef.current?.srcObject as MediaStream;
    stream?.getTracks().forEach((track) => track.stop());
    if (videoRef.current) videoRef.current.srcObject = null;
    if (intervalRef.current) clearInterval(intervalRef.current);
    setCameraStatus("stopped");
  };

  const capture = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas || cameraStatus !== "active") return;

    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Draw rectangles and IDs
    facesData.forEach((face) => {
      const [x, y, w, h] = face.box;
      ctx.strokeStyle = face.match ? "lime" : "red";
      ctx.lineWidth = 2;
      ctx.strokeRect(x, y, w, h);

      if (face.match) {
        ctx.fillStyle = "lime";
        ctx.font = "16px Arial";
        ctx.fillText(`${face.match.name} (${face.match.user_id})`, x, y - 5);
      } else {
        ctx.fillStyle = "red";
        ctx.font = "16px Arial";
        ctx.fillText("Unknown", x, y - 5);
      }
    });

    const dataUrl = canvas.toDataURL("image/jpeg", 0.8);
    onCapture(dataUrl);
  };

  useEffect(() => {
    if (singleShot || isLiveMode) startCamera();
    return () => stopCamera();
  }, [singleShot, isLiveMode]);

  useEffect(() => {
    if (intervalRef.current) clearInterval(intervalRef.current);
    if (captureIntervalMs && isLiveMode && cameraStatus === "active") {
      intervalRef.current = setInterval(capture, captureIntervalMs);
    }
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [captureIntervalMs, isLiveMode, cameraStatus, facesData]);

  return (
    <div className="relative w-full max-w-md">
      <video
        ref={videoRef}
        autoPlay
        muted
        playsInline
        className={`rounded-lg shadow-md w-full ${cameraStatus === "active" ? "block" : "hidden"}`}
        style={{ maxHeight: "360px" }}
      />
      <canvas ref={canvasRef} className="absolute top-0 left-0 rounded-lg w-full" />
      
      {cameraStatus === "loading" && (
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-white bg-opacity-90 p-4 rounded-lg text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
          <p className="text-gray-700">Starting camera...</p>
        </div>
      )}
      
      {cameraStatus === "stopped" && !cameraError && (
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-white bg-opacity-90 p-4 rounded-lg text-center">
          <button
            onClick={startCamera}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
          >
            Start Camera
          </button>
        </div>
      )}
      
      {cameraError && (
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-white bg-opacity-95 p-6 rounded-lg text-center max-w-sm shadow-lg">
          <div className="text-red-600 mb-4">
            <svg className="w-12 h-12 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            <p className="text-sm font-medium">{cameraError}</p>
          </div>
          
          <div className="text-xs text-gray-600 mb-4 text-left">
            <p className="font-medium mb-2">Troubleshooting steps:</p>
            <ul className="list-disc list-inside space-y-1">
              <li>Check browser permissions (click 🔒 in address bar)</li>
              <li>Close other apps using the camera</li>
              <li>Try refreshing the page</li>
              <li>Use HTTPS instead of HTTP if possible</li>
              <li>Try a different browser (Chrome/Edge recommended)</li>
            </ul>
          </div>
          
          <button
            onClick={startCamera}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            Try Again
          </button>
        </div>
      )}
    </div>
  );
};

export default CameraCapture;
