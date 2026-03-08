import { useState } from 'react';
import { Link } from 'react-router-dom';
import UploadZone from '../components/UploadZone';
import ResultCard from '../components/ResultCard';
import ReportDetails from '../components/ReportDetails';

export default function Dashboard() {
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleResult = (data) => {
    setError('');
    setResult(data.scan);
  };

  const handleError = (msg) => {
    setResult(null);
    setError(msg);
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Deepfake Analysis</h1>
        <p className="text-slate-400 mt-1">Upload media to detect deepfakes, or paste any URL to check if it's fake or real</p>
      </div>

      <UploadZone onResult={handleResult} onError={handleError} />

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 text-red-400 px-6 py-4 rounded-xl">
          {error}
        </div>
      )}

      {result && (
        <>
          <ResultCard scan={result} />
          <ReportDetails report={result.detailed_report} />
          <div className="text-center">
            <Link to={`/report/${result.id}`} className="text-blue-400 hover:text-blue-300 text-sm">
              View full report page
            </Link>
          </div>
        </>
      )}
    </div>
  );
}
