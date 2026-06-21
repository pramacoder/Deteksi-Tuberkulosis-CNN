"use client";

import React, { useState } from 'react';
import UploadZone from '@/components/UploadZone';
import ResultCard from '@/components/ResultCard';
import GradcamViewer from '@/components/GradcamViewer';
import { predictWithGradcam, GradcamResponse } from '@/lib/api';
import { Activity, Loader2 } from 'lucide-react';

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<GradcamResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelect = (selectedFile: File) => {
    setFile(selectedFile);
    setPreview(URL.createObjectURL(selectedFile));
    setResult(null);
    setError(null);
  };

  const handleAnalyze = async () => {
    if (!file) return;

    setIsLoading(true);
    setError(null);

    try {
      const res = await predictWithGradcam(file);
      setResult(res);
    } catch (err: any) {
      setError(err.message || "Terjadi kesalahan saat menghubungi server.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-slate-950 text-slate-200 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Header Section */}
        <div className="text-center mb-10">
          <div className="flex justify-center mb-4">
            <div className="p-3 bg-blue-500/20 rounded-full border border-blue-500/30">
              <Activity className="w-10 h-10 text-blue-400" />
            </div>
          </div>
          <h1 className="text-4xl font-bold text-white mb-4 tracking-tight">
            Deteksi Tuberkulosis (TB)
          </h1>
          <p className="text-lg text-slate-400 max-w-2xl mx-auto">
            Sistem analisis citra Chest X-Ray berbasis AI (Convolutional Neural Network) 
            untuk skrining awal penyakit Tuberkulosis.
          </p>
        </div>

        {/* Upload Section */}
        <div className="bg-slate-900 border border-slate-800 p-6 md:p-8 rounded-2xl shadow-xl">
          <UploadZone onFileSelect={handleFileSelect} isLoading={isLoading} />
          
          <div className="mt-6 flex justify-center">
            <button
              onClick={handleAnalyze}
              disabled={!file || isLoading}
              className={`px-8 py-3 rounded-lg font-semibold flex items-center space-x-2 transition-all duration-200 ${
                !file || isLoading
                  ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-500/20 hover:shadow-blue-500/40 transform hover:-translate-y-0.5'
              }`}
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Menganalisa...</span>
                </>
              ) : (
                <>
                  <Activity className="w-5 h-5" />
                  <span>Mulai Analisis AI</span>
                </>
              )}
            </button>
          </div>
          
          {error && (
            <div className="mt-4 p-4 bg-red-500/10 border border-red-500/50 rounded-lg text-red-400 text-sm text-center">
              {error}
            </div>
          )}
        </div>

        {/* Results Section */}
        {result && (
          <div className="mt-8 space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <ResultCard result={result} />
            <GradcamViewer 
              originalImageSrc={preview} 
              gradcamImageSrc={result.gradcam_image} 
            />
          </div>
        )}
      </div>
    </main>
  );
}
