import React, { useCallback, useState } from 'react';
import { UploadCloud, File, Loader2 } from 'lucide-react';

export default function UploadZone({ onUpload, isUploading }) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) {
      setSelectedFile(file);
      onUpload(file);
    }
  }, [onUpload]);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      onUpload(file);
    }
  };

  return (
    <div className="animate-in fade-in slide-in-from-bottom-4 duration-700 delay-150">
      <div 
        onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
        onDragLeave={() => setIsDragOver(false)}
        onDrop={handleDrop}
        className={`relative w-full max-w-2xl mx-auto rounded-2xl p-10 flex flex-col items-center justify-center text-center transition-all duration-300 border-2 border-dashed
          ${isDragOver 
            ? 'border-primary bg-primary/5 scale-[1.02]' 
            : 'border-white/20 bg-black/40 hover:bg-white/5'
          }
          backdrop-blur-md`}
        style={isDragOver ? { boxShadow: '0 0 30px rgba(34, 197, 94, 0.2)' } : {}}
      >
        <input 
          type="file" 
          onChange={handleFileChange} 
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          accept="image/*,.pdf"
          disabled={isUploading}
        />
        
        {isUploading ? (
          <div className="flex flex-col items-center space-y-4">
            <Loader2 className="w-12 h-12 text-primary animate-spin" />
            <div className="space-y-1">
              <h3 className="text-lg font-semibold text-white tracking-tight">Extracting Data...</h3>
              <p className="text-sm text-gray-400">Lexion LayoutLM is processing your document</p>
            </div>
          </div>
        ) : selectedFile ? (
          <div className="flex flex-col items-center space-y-4">
            <div className="p-4 rounded-full bg-primary/20">
              <File className="w-10 h-10 text-primary" />
            </div>
            <div className="space-y-1">
              <h3 className="text-lg font-semibold text-white tracking-tight">{selectedFile.name}</h3>
              <p className="text-sm text-gray-400">Click or drag to upload another</p>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center space-y-4 group">
            <div className="p-4 rounded-full bg-white/5 border border-white/10 group-hover:border-primary/50 transition-colors">
              <UploadCloud className="w-10 h-10 text-gray-400 group-hover:text-primary transition-colors" />
            </div>
            <div className="space-y-1">
              <h3 className="text-lg font-semibold text-white tracking-tight">Upload Document</h3>
              <p className="text-sm text-gray-400">Drag & drop your invoice, receipt, or form here</p>
            </div>
            <button className="mt-4 px-6 py-2 rounded-lg bg-primary text-white font-medium hover:bg-primary/90 transition-colors" style={{ boxShadow: '0 0 15px rgba(34, 197, 94, 0.4)' }}>
              Browse Files
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
