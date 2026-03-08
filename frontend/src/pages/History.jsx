import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { FiTrash2, FiEye, FiVideo, FiMic, FiBarChart2 } from 'react-icons/fi';
import { reportAPI } from '../services/api';

export default function History() {
  const [scans, setScans] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [historyRes, statsRes] = await Promise.all([
          reportAPI.getHistory(),
          reportAPI.getStats(),
        ]);
        setScans(historyRes.data.scans);
        setStats(statsRes.data);
      } catch (err) {
        console.error('Failed to load history:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this scan?')) return;
    try {
      await reportAPI.deleteReport(id);
      setScans(scans.filter((s) => s.id !== id));
    } catch (err) {
      alert('Failed to delete scan');
    }
  };

  const riskColor = (risk) => {
    const map = { Critical: 'text-red-400', High: 'text-orange-400', Medium: 'text-yellow-400', Low: 'text-green-400' };
    return map[risk] || 'text-slate-400';
  };

  const riskBg = (risk) => {
    const map = { Critical: 'bg-red-500/10', High: 'bg-orange-500/10', Medium: 'bg-yellow-500/10', Low: 'bg-green-500/10' };
    return map[risk] || 'bg-slate-500/10';
  };

  if (loading) {
    return <div className="max-w-5xl mx-auto px-4 py-8 text-center py-20 text-slate-400">Loading...</div>;
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-8">
      <h1 className="text-3xl font-bold">Scan History</h1>

      {/* Stats */}
      {stats && stats.total_scans > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="card p-4 text-center">
            <p className="text-2xl font-bold text-blue-400">{stats.total_scans}</p>
            <p className="text-xs text-slate-400">Total Scans</p>
          </div>
          <div className="card p-4 text-center">
            <p className="text-2xl font-bold text-red-400">{stats.avg_fake_percentage}%</p>
            <p className="text-xs text-slate-400">Avg Fake Score</p>
          </div>
          <div className="card p-4 text-center">
            <p className="text-2xl font-bold text-purple-400">{stats.file_type_distribution?.video || 0}</p>
            <p className="text-xs text-slate-400">Videos Analyzed</p>
          </div>
          <div className="card p-4 text-center">
            <p className="text-2xl font-bold text-cyan-400">{stats.file_type_distribution?.audio || 0}</p>
            <p className="text-xs text-slate-400">Audios Analyzed</p>
          </div>
        </div>
      )}

      {/* Scan List */}
      {scans.length === 0 ? (
        <div className="card p-12 text-center">
          <FiBarChart2 className="mx-auto text-slate-600 mb-4" size={48} />
          <p className="text-slate-400">No scans yet. Upload a file to get started.</p>
          <Link to="/dashboard" className="btn-primary inline-block mt-4 no-underline">
            Start Analyzing
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {scans.map((scan) => (
            <div key={scan.id} className="card p-4 flex items-center justify-between hover:border-slate-500/30 transition">
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-lg bg-slate-800 flex items-center justify-center">
                  {scan.file_type === 'video' ? <FiVideo className="text-blue-400" /> : <FiMic className="text-purple-400" />}
                </div>
                <div>
                  <p className="font-medium text-sm">{scan.filename}</p>
                  <p className="text-xs text-slate-500">
                    {new Date(scan.created_at).toLocaleDateString()} &middot; {scan.source_type}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-6">
                <div className="text-right">
                  <p className="text-sm font-semibold">
                    <span className="text-red-400">{scan.fake_percentage}%</span>
                    <span className="text-slate-500 mx-1">/</span>
                    <span className="text-green-400">{scan.real_percentage}%</span>
                  </p>
                  <span className={`text-xs font-semibold ${riskColor(scan.risk_level)} ${riskBg(scan.risk_level)} px-2 py-0.5 rounded-full`}>
                    {scan.risk_level}
                  </span>
                </div>

                <div className="flex gap-2">
                  <Link to={`/report/${scan.id}`} className="text-slate-400 hover:text-blue-400 transition p-2">
                    <FiEye size={16} />
                  </Link>
                  <button onClick={() => handleDelete(scan.id)} className="text-slate-400 hover:text-red-400 transition bg-transparent border-0 cursor-pointer p-2">
                    <FiTrash2 size={16} />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
