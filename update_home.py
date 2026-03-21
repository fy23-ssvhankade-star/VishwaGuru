import re

with open('frontend/src/views/Home.jsx', 'r') as f:
    content = f.read()

content = content.replace('''  return (
    <div className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl p-6 w-full max-w-sm text-center">
        <h3 className="text-lg font-bold mb-4">Camera Diagnostics</h3>
        <div className="bg-gray-100 rounded-lg h-48 mb-4 flex items-center justify-center overflow-hidden relative">
          {status === 'requesting' && <span className="text-gray-500 animate-pulse">Requesting access...</span>}
          {status === 'error' && <span className="text-red-500 font-medium">Camera access failed. Check permissions.</span>}
          <video ref={videoRef} autoPlay playsInline className={`w-full h-full object-cover ${status === 'active' ? 'block' : 'hidden'}`} />
        </div>
        {status === 'active' && <p className="text-green-600 font-medium text-sm mb-4">Camera is working correctly!</p>}
        <button onClick={onClose} className="w-full bg-blue-600 text-white py-2 rounded-lg font-bold">Close</button>
      </div>
    </div>
  );''', '''  return createPortal(
    <div className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl p-6 w-full max-w-sm text-center">
        <h3 className="text-lg font-bold mb-4">Camera Diagnostics</h3>
        <div className="bg-gray-100 rounded-lg h-48 mb-4 flex items-center justify-center overflow-hidden relative">
          {status === 'requesting' && <span className="text-gray-500 animate-pulse">Requesting access...</span>}
          {status === 'error' && <span className="text-red-500 font-medium">Camera access failed. Check permissions.</span>}
          <video ref={videoRef} autoPlay playsInline className={`w-full h-full object-cover ${status === 'active' ? 'block' : 'hidden'}`} />
        </div>
        {status === 'active' && <p className="text-green-600 font-medium text-sm mb-4">Camera is working correctly!</p>}
        <button onClick={onClose} className="w-full bg-blue-600 text-white py-2 rounded-lg font-bold">Close</button>
      </div>
    </div>,
    document.body
  );''')

# Also, looking for any other fixes
content = content.replace("className={`w-full h-full object-cover ${status === 'active' ? 'block' : 'hidden'}`}", "className={`w-full h-full object-cover ${status === 'active' ? 'block' : 'hidden'}`}")

with open('frontend/src/views/Home.jsx', 'w') as f:
    f.write(content)
