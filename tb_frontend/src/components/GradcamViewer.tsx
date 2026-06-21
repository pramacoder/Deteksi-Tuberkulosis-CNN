import React, { useState } from 'react';
import { Eye, EyeOff } from 'lucide-react';

interface GradcamViewerProps {
  originalImageSrc: string | null;
  gradcamImageSrc: string | null;
}

export default function GradcamViewer({ originalImageSrc, gradcamImageSrc }: GradcamViewerProps) {
  const [showOverlay, setShowOverlay] = useState(true);

  if (!originalImageSrc || !gradcamImageSrc) return null;

  return (
    <div className="w-full mt-6 bg-slate-800 border border-slate-700 rounded-xl shadow-lg overflow-hidden">
      <div className="flex justify-between items-center p-4 border-b border-slate-700 bg-slate-800/50">
        <h3 className="text-md font-medium text-slate-200">
          Grad-CAM Heatmap Analysis
        </h3>
        <button
          onClick={() => setShowOverlay(!showOverlay)}
          className="flex items-center space-x-2 text-sm px-3 py-1.5 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors text-slate-200"
        >
          {showOverlay ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          <span>{showOverlay ? 'Hide Overlay' : 'Show Overlay'}</span>
        </button>
      </div>
      
      <div className="p-6">
        <div className="relative w-full max-w-2xl mx-auto aspect-square rounded-lg overflow-hidden border-2 border-slate-700 bg-black">
          {/* Original Image */}
          <img 
            src={originalImageSrc} 
            alt="Original X-Ray" 
            className="absolute inset-0 w-full h-full object-contain"
          />
          
          {/* Grad-CAM Overlay */}
          <img 
            src={gradcamImageSrc} 
            alt="Grad-CAM Overlay" 
            className={`absolute inset-0 w-full h-full object-contain transition-opacity duration-300 ${
              showOverlay ? 'opacity-100' : 'opacity-0'
            }`}
          />
        </div>
        
        <p className="mt-4 text-sm text-slate-400 text-center max-w-2xl mx-auto">
          Heatmap (Grad-CAM) menunjukkan area pada gambar X-Ray yang paling berpengaruh terhadap keputusan model. 
          Area berwarna merah/panas mengindikasikan fitur yang kuat terkait Tuberkulosis.
        </p>
      </div>
    </div>
  );
}
