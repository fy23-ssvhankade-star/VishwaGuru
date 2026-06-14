import React, { useState, useRef, useCallback } from 'react';
import Webcam from 'react-webcam';

const PlaygroundDetector = ({ onBack }) => {
  const webcamRef = useRef(null);
  const [imgSrc, setImgSrc] = useState(null);
  const [detections, setDetections] = useState([]);
  const [loading, setLoading] = useState(false);
  const [cameraError, setCameraError] = useState(null);

  const capture = useCallback(() => {
    const imageSrc = webcamRef.current.getScreenshot();
    setImgSrc(imageSrc);
  }, [webcamRef]);

  const retake = () => {
    setImgSrc(null);
    setDetections([]);
  };

  const detectPlaygroundDamage = async () => {
    if (!imgSrc) return;
    setLoading(true);
    setDetections([]);

    try {
        // Convert base64 to blob
        const res = await fetch(imgSrc);
        const blob = await res.blob();
        const file = new File([blob], "image.jpg", { type: "image/jpeg" });

        const formData = new FormData();
        formData.append('image', file);

        // Call Backend API
        const response = await fetch('/api/detect-playground', {
            method: 'POST',
            body: formData,
        });

        if (response.ok) {
            const data = await response.json();
            setDetections(data.detections);
            if (data.detections.length === 0) {
                alert("No playground issues detected.");
            }
        } else {
            console.error("Detection failed");
            alert("Detection failed. Please try again.");
        }
    } catch (error) {
        console.error("Error:", error);
        alert("An error occurred during detection.");
    } finally {
        setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full p-4">
      <button onClick={onBack} className="self-start text-blue-600 mb-4 font-semibold flex items-center">
        &larr; Back to Home
      </button>
      <div className="max-w-md mx-auto w-full bg-white rounded-xl shadow-lg p-6">
        <h2 className="text-2xl font-bold mb-4 text-center text-gray-800">Playground Safety Check</h2>
        <p className="text-gray-500 text-sm text-center mb-6">
          Detect damaged equipment, broken swings, or unsafe slides.
        </p>

        {cameraError ? (
            <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg text-sm text-center">
                <strong className="font-bold block mb-1">Camera Error</strong>
                {cameraError}
            </div>
        ) : (
            <div className="mb-6 rounded-xl overflow-hidden shadow-inner border border-gray-200 bg-gray-100 min-h-[300px] relative">
              {!imgSrc ? (
                <Webcam
                  audio={false}
                  ref={webcamRef}
                  screenshotFormat="image/jpeg"
                  className="w-full h-full object-cover"
                  onUserMediaError={() => setCameraError("Could not access camera. Please check permissions.")}
                  videoConstraints={{ facingMode: "environment" }}
                />
              ) : (
                <div className="relative">
                    <img src={imgSrc} alt="Captured" className="w-full" />
                    {detections.length > 0 && (
                        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4">
                             <div className="flex flex-wrap gap-2">
                                {detections.map((d, idx) => (
                                    <span key={idx} className="bg-red-500 text-white text-xs px-2 py-1 rounded-full font-bold shadow-sm">
                                        {d.label} ({(d.confidence * 100).toFixed(0)}%)
                                    </span>
                                ))}
                             </div>
                        </div>
                    )}
                </div>
              )}
            </div>
        )}

        <div className="flex justify-center gap-4">
          {!imgSrc ? (
            <button
              onClick={capture}
              disabled={!!cameraError}
              className={`flex-1 bg-blue-600 text-white py-3 rounded-xl font-bold shadow-md hover:bg-blue-700 transition transform active:scale-95 ${cameraError ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              Capture Photo
            </button>
          ) : (
            <>
              <button
                onClick={retake}
                className="flex-1 bg-gray-100 text-gray-700 py-3 rounded-xl font-bold hover:bg-gray-200 transition"
              >
                Retake
              </button>
              <button
                onClick={detectPlaygroundDamage}
                disabled={loading}
                className={`flex-1 bg-blue-600 text-white py-3 rounded-xl font-bold shadow-md hover:bg-blue-700 transition flex items-center justify-center gap-2 ${loading ? 'opacity-70 cursor-wait' : ''}`}
              >
                {loading ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white/50 border-t-white rounded-full animate-spin"></div>
                      Checking...
                    </>
                ) : 'Analyze'}
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default PlaygroundDetector;
