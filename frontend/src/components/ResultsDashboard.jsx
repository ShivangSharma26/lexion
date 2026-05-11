import React from 'react';
import { CheckCircle2, AlertTriangle, Layers } from 'lucide-react';

export default function ResultsDashboard({ results }) {
  if (!results || results.length === 0) return null;

  // Build a structured JSON payload for enterprise view
  const structuredJson = {};
  
  results.forEach(item => {
    if (item.type === 'PAIRED') {
      const key = item.question;
      const value = item.answer || null;
      
      if (structuredJson[key] !== undefined) {
        if (Array.isArray(structuredJson[key])) {
          structuredJson[key].push(value);
        } else {
          structuredJson[key] = [structuredJson[key], value];
        }
      } else {
        structuredJson[key] = value;
      }
    } else if (item.type === 'HEADER') {
      if (!structuredJson["_HEADERS"]) structuredJson["_HEADERS"] = [];
      structuredJson["_HEADERS"].push(item.value);
    } else if (item.type === 'UNPAIRED_ANSWER') {
      if (!structuredJson["_UNMATCHED_DATA"]) structuredJson["_UNMATCHED_DATA"] = [];
      structuredJson["_UNMATCHED_DATA"].push(item.value);
    }
  });

  return (
    <div className="w-full mx-auto mt-12 animate-in fade-in slide-in-from-bottom-8 duration-700">
      <div className="flex items-center gap-3 mb-6">
        <Layers className="w-6 h-6 text-primary" />
        <h2 className="text-2xl font-bold tracking-tight text-white">Extracted Entities</h2>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Left Side: Visual Table */}
        <div className="bg-black/40 backdrop-blur-md border border-white/10 rounded-2xl overflow-hidden shadow-2xl flex flex-col h-[600px]">
          <div className="grid grid-cols-12 gap-4 p-4 border-b border-white/10 bg-white/5 font-semibold text-sm text-gray-300">
            <div className="col-span-5">Question (Key)</div>
            <div className="col-span-5">Answer (Value)</div>
            <div className="col-span-2 text-right">Conf</div>
          </div>
          
          <div className="divide-y divide-white/5 flex-1 overflow-y-auto custom-scrollbar">
            {results.map((item, idx) => (
              <div key={idx} className="grid grid-cols-12 gap-4 p-4 items-center hover:bg-white/5 transition-colors group">
                <div className="col-span-5 text-emerald-400 font-medium break-words pr-2 text-sm">
                  {item.type === 'PAIRED' ? item.question : (item.type === 'HEADER' ? `[HEADER] ${item.value}` : item.type)}
                </div>
                <div className="col-span-5 text-white font-medium break-words text-sm">
                  {item.type === 'PAIRED' ? (item.answer || "—") : (item.type === 'UNPAIRED_ANSWER' ? item.value : "—")}
                </div>
                <div className="col-span-2 flex items-center justify-end gap-1">
                  <span className="text-xs font-mono text-gray-400">{(item.confidence * 100).toFixed(0)}%</span>
                  {item.confidence > 0.8 ? (
                    <CheckCircle2 className="w-3 h-3 text-green-500" />
                  ) : (
                    <AlertTriangle className="w-3 h-3 text-yellow-500" />
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Side: Enterprise JSON Payload */}
        <div className="bg-black/60 backdrop-blur-md border border-white/10 rounded-2xl p-6 shadow-2xl flex flex-col h-[600px]">
          <div className="mb-4">
            <h3 className="text-lg font-bold text-white mb-1">Enterprise JSON Payload</h3>
            <p className="text-xs text-gray-400">Ready for automated database ingestion</p>
          </div>
          <div className="flex-1 overflow-auto rounded-xl bg-[#050505] border border-white/5 p-4 custom-scrollbar">
            <pre className="text-sm font-mono text-emerald-400 whitespace-pre-wrap leading-relaxed">
              {JSON.stringify(structuredJson, null, 2)}
            </pre>
          </div>
        </div>

      </div>
    </div>
  );
}
