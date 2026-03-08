import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { FiArrowLeft } from 'react-icons/fi';
import { reportAPI } from '../services/api';
import ResultCard from '../components/ResultCard';
import ReportDetails from '../components/ReportDetails';

export default function Report() {
  const { id } = useParams();
  const [scan, setScan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchReport = async () => {
      try {
        const res = await reportAPI.getReport(id);
        setScan(res.data.scan);
      } catch (err) {
        setError(err.response?.data?.error || 'Failed to load report');
      } finally {
        setLoading(false);
      }
    };
    fetchReport();
  }, [id]);

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-8">
        <div className="text-center py-20 text-slate-400">Loading report...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-8">
        <div className="bg-red-500/10 border border-red-500/30 text-red-400 px-6 py-4 rounded-xl">{error}</div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-8">
      <div className="flex items-center gap-4">
        <Link to="/history" className="text-slate-400 hover:text-white transition">
          <FiArrowLeft size={20} />
        </Link>
        <div>
          <h1 className="text-3xl font-bold">Analysis Report</h1>
          <p className="text-slate-400 text-sm mt-1">
            Scanned on {new Date(scan.created_at).toLocaleDateString('en-US', {
              year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit'
            })}
          </p>
        </div>
      </div>

      <ResultCard scan={scan} />
      <ReportDetails report={scan.detailed_report} />
    </div>
  );
}
