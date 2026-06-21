import React from 'react';
import { PredictResponse } from '@/lib/api';
import { AlertTriangle, CheckCircle2 } from 'lucide-react';

interface ResultCardProps {
  result: PredictResponse | null;
}

export default function ResultCard({ result }: ResultCardProps) {
  if (!result) return null;

  const isTB = result.label === "TB";
  
  return (
    <div className="w-full p-6 bg-slate-800 border border-slate-700 rounded-xl shadow-lg mt-6">
      <h3 className="text-lg font-medium text-slate-200 mb-4 border-b border-slate-700 pb-2">
        Hasil Analisis
      </h3>
      
      <div className="flex flex-col md:flex-row gap-6 items-center">
        {/* Diagnosis Badge */}
        <div className={`flex flex-col items-center justify-center p-6 rounded-xl border-2 w-full md:w-1/3 ${
          isTB 
            ? 'bg-red-500/10 border-red-500/50 text-red-400' 
            : 'bg-green-500/10 border-green-500/50 text-green-400'
        }`}>
          {isTB ? <AlertTriangle className="w-12 h-12 mb-2" /> : <CheckCircle2 className="w-12 h-12 mb-2" />}
          <span className="text-2xl font-bold uppercase tracking-wider">{result.label}</span>
          <span className="text-xs mt-1 opacity-80 text-center">
            Berdasarkan threshold {result.threshold_used}
          </span>
        </div>

        {/* Probabilitas & Confidence */}
        <div className="flex-1 w-full space-y-4">
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-slate-400">Probabilitas TB</span>
              <span className="font-medium text-slate-200">{(result.probability * 100).toFixed(1)}%</span>
            </div>
            <div className="w-full h-3 bg-slate-900 rounded-full overflow-hidden">
              <div 
                className={`h-full rounded-full ${isTB ? 'bg-red-500' : 'bg-green-500'}`}
                style={{ width: `${result.probability * 100}%` }}
              ></div>
            </div>
          </div>

          <div className="flex justify-between items-center bg-slate-900/50 p-3 rounded-lg border border-slate-700">
            <span className="text-sm text-slate-400">Tingkat Kepercayaan Model:</span>
            <span className={`px-3 py-1 text-xs font-semibold rounded-full ${
              result.confidence === 'High' ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30' :
              result.confidence === 'Medium' ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30' :
              'bg-slate-500/20 text-slate-400 border border-slate-500/30'
            }`}>
              {result.confidence.toUpperCase()}
            </span>
          </div>
        </div>
      </div>

      <div className="mt-6 text-xs text-slate-500 bg-slate-900/30 p-3 rounded-lg border border-slate-800">
        <strong>Disclaimer Medis:</strong> Hasil analisis ini dihasilkan oleh model AI (BasicCNN) untuk tujuan skrining awal. 
        Ini bukan diagnosis definitif. Selalu konsultasikan dengan dokter atau profesional medis untuk diagnosis yang akurat.
      </div>
    </div>
  );
}
