"use client";

import React, { useCallback, useState } from 'react';
import { UploadCloud, FileImage, X } from 'lucide-react';

interface UploadZoneProps {
  onFileSelect: (file: File) => void;
  isLoading: boolean;
}

export default function UploadZone({ onFileSelect, isLoading }: UploadZoneProps) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (file: File) => {
    if (!file.type.startsWith('image/')) {
      alert('Tolong unggah file gambar yang valid.');
      return;
    }
    setSelectedFile(file);
    const objectUrl = URL.createObjectURL(file);
    setPreview(objectUrl);
    onFileSelect(file);
  };

  const clearFile = () => {
    setSelectedFile(null);
    setPreview(null);
  };

  return (
    <div className="w-full">
      {!selectedFile ? (
        <div
          className={`relative flex flex-col items-center justify-center w-full h-64 border-2 border-dashed rounded-xl transition-colors duration-200 ease-in-out cursor-pointer ${
            dragActive ? 'border-blue-500 bg-blue-500/10' : 'border-slate-600 bg-slate-800 hover:bg-slate-700/50 hover:border-slate-500'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <input
            type="file"
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            onChange={handleChange}
            accept="image/*"
            disabled={isLoading}
          />
          <UploadCloud className="w-12 h-12 mb-4 text-slate-400" />
          <p className="mb-2 text-sm text-slate-300">
            <span className="font-semibold">Klik untuk unggah</span> atau drag and drop
          </p>
          <p className="text-xs text-slate-500">PNG, JPG atau JPEG (Maks. 10MB)</p>
        </div>
      ) : (
        <div className="relative w-full overflow-hidden border border-slate-700 rounded-xl bg-slate-800">
          <button
            onClick={clearFile}
            className="absolute top-2 right-2 p-1.5 bg-slate-900/80 hover:bg-red-500/80 rounded-full text-white transition-colors z-10"
            disabled={isLoading}
          >
            <X className="w-4 h-4" />
          </button>
          <div className="flex flex-col items-center p-4">
            {preview && (
              <img 
                src={preview} 
                alt="Preview" 
                className="max-h-64 object-contain rounded-lg mb-4"
              />
            )}
            <div className="flex items-center text-sm text-slate-300">
              <FileImage className="w-4 h-4 mr-2" />
              {selectedFile.name}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
