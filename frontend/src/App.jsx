import React, { useState } from 'react';
import Header from './components/Header';
import UploadZone from './components/UploadZone';
import ResultsDashboard from './components/ResultsDashboard';
import { AlertCircle } from 'lucide-react';

function App() {
  const [results, setResults] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState(null);

  const handleUpload = async (file) => {
    setIsUploading(true);
    setError(null);
    setResults(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      // Connect to FastAPI backend running on port 8000
      const response = await fetch('http://localhost:8000/extract', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }

      const data = await response.json();
      if (data.error) {
        throw new Error(data.error);
      }

      setResults(data.entities);
    } catch (err) {
      console.error(err);
      setError(err.message || 'An error occurred during extraction');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-gray-100 selection:bg-primary/30 relative overflow-x-hidden">
      {/* Deep Space Background Gradients */}
      <div className="fixed top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[500px] bg-primary/10 rounded-full blur-[120px] pointer-events-none opacity-50 z-0" />
      <div className="fixed bottom-0 right-0 w-[800px] h-[600px] bg-green-900/10 rounded-full blur-[150px] pointer-events-none opacity-30 z-0" />

      <Header />

      <main className="container mx-auto px-4 py-16 relative z-10">
        <div className="max-w-3xl mx-auto text-center mb-12 animate-in fade-in slide-in-from-bottom-4 duration-700">
          <h2 className="text-4xl md:text-5xl font-extrabold tracking-tight text-white mb-4">
            Document Intelligence. <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-emerald-400">Evolved.</span>
          </h2>
          <p className="text-lg text-gray-400">
            Powered by LayoutLM. Upload an invoice, receipt, or form to instantly extract structured JSON data using spatial awareness.
          </p>
        </div>

        <UploadZone onUpload={handleUpload} isUploading={isUploading} />

        {error && (
          <div className="max-w-2xl mx-auto mt-8 p-4 rounded-xl bg-red-500/10 border border-red-500/20 flex items-start gap-3 animate-in fade-in">
            <AlertCircle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
            <div>
              <h4 className="text-sm font-semibold text-red-500">Extraction Failed</h4>
              <p className="text-sm text-red-400/80">{error}</p>
            </div>
          </div>
        )}

        <ResultsDashboard results={results} />
      </main>
    </div>
  );
}

export default App;
