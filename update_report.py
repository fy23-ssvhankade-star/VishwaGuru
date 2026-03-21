import re

with open('frontend/src/views/ReportForm.jsx', 'r') as f:
    content = f.read()

# Make sure react-dom createPortal is imported
if 'createPortal' not in content:
    content = content.replace("import React, { useState, useEffect } from 'react';", "import React, { useState, useEffect } from 'react';\nimport { createPortal } from 'react-dom';")

content = content.replace('''              {showWebcam && (
                <div className="fixed inset-0 z-50 bg-black/90 flex flex-col items-center justify-center p-4">
                  <div className="relative w-full max-w-md bg-black rounded-3xl overflow-hidden border border-gray-800">
                    <Webcam
                      audio={false}
                      ref={webcamRef}
                      screenshotFormat="image/jpeg"
                      videoConstraints={{ facingMode: "environment" }}
                      className="w-full object-cover aspect-[3/4]"
                    />
                    <div className="absolute bottom-0 left-0 right-0 p-6 bg-gradient-to-t from-black/80 to-transparent flex justify-center gap-6">
                      <button
                        type="button"
                        onClick={() => setShowWebcam(false)}
                        className="p-4 bg-gray-800 text-white rounded-full hover:bg-gray-700 transition"
                      >
                        Cancel
                      </button>
                      <button
                        type="button"
                        onClick={captureWebcam}
                        className="p-4 bg-blue-600 text-white rounded-full hover:bg-blue-500 transition shadow-lg shadow-blue-500/50"
                      >
                        <Camera size={24} />
                      </button>
                    </div>
                  </div>
                </div>
              )}''', '''              {showWebcam && createPortal(
                <div className="fixed inset-0 z-50 bg-black/90 flex flex-col items-center justify-center p-4">
                  <div className="relative w-full max-w-md bg-black rounded-3xl overflow-hidden border border-gray-800">
                    <Webcam
                      audio={false}
                      ref={webcamRef}
                      screenshotFormat="image/jpeg"
                      videoConstraints={{ facingMode: "environment" }}
                      className="w-full object-cover aspect-[3/4]"
                    />
                    <div className="absolute bottom-0 left-0 right-0 p-6 bg-gradient-to-t from-black/80 to-transparent flex justify-center gap-6">
                      <button
                        type="button"
                        onClick={() => setShowWebcam(false)}
                        className="p-4 bg-gray-800 text-white rounded-full hover:bg-gray-700 transition"
                      >
                        Cancel
                      </button>
                      <button
                        type="button"
                        onClick={captureWebcam}
                        className="p-4 bg-blue-600 text-white rounded-full hover:bg-blue-500 transition shadow-lg shadow-blue-500/50"
                      >
                        <Camera size={24} />
                      </button>
                    </div>
                  </div>
                </div>, document.body
              )}''')

with open('frontend/src/views/ReportForm.jsx', 'w') as f:
    f.write(content)
