import { Bar, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Title, Tooltip, Legend);

export default function ReportDetails({ report }) {
  if (!report) return null;

  const summary = report.analysis_summary || {};
  const metadata = report.metadata || {};

  // Doughnut chart for fake/real
  const doughnutData = {
    labels: ['Fake', 'Real'],
    datasets: [{
      data: [report.fake_percentage, report.real_percentage],
      backgroundColor: ['#ef4444', '#22c55e'],
      borderWidth: 0,
    }],
  };

  // Bar chart for analysis breakdown
  const barLabels = [];
  const barValues = [];
  Object.entries(summary).forEach(([key, value]) => {
    barLabels.push(key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()));
    barValues.push(value);
  });

  const barData = {
    labels: barLabels,
    datasets: [{
      label: 'Score (%)',
      data: barValues,
      backgroundColor: barValues.map(v => v > 60 ? 'rgba(239,68,68,0.7)' : v > 30 ? 'rgba(234,179,8,0.7)' : 'rgba(34,197,94,0.7)'),
      borderRadius: 6,
    }],
  };

  const barOptions = {
    responsive: true,
    plugins: { legend: { display: false } },
    scales: {
      y: { beginAtZero: true, max: 100, grid: { color: '#334155' }, ticks: { color: '#94a3b8' } },
      x: { grid: { display: false }, ticks: { color: '#94a3b8', maxRotation: 45 } },
    },
  };

  const doughnutOptions = {
    responsive: true,
    plugins: { legend: { position: 'bottom', labels: { color: '#e2e8f0' } } },
    cutout: '60%',
  };

  return (
    <div className="space-y-6">
      {/* Charts Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card p-6">
          <h3 className="text-lg font-semibold mb-4">Detection Result</h3>
          <div className="max-w-[250px] mx-auto">
            <Doughnut data={doughnutData} options={doughnutOptions} />
          </div>
        </div>

        {barLabels.length > 0 && (
          <div className="card p-6">
            <h3 className="text-lg font-semibold mb-4">Analysis Breakdown</h3>
            <Bar data={barData} options={barOptions} />
          </div>
        )}
      </div>

      {/* Metadata */}
      {Object.keys(metadata).length > 0 && (
        <div className="card p-6">
          <h3 className="text-lg font-semibold mb-4">File Metadata</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {metadata.duration != null && (
              <div className="bg-slate-800/50 rounded-lg p-3">
                <p className="text-xs text-slate-400">Duration</p>
                <p className="text-lg font-semibold">{metadata.duration}s</p>
              </div>
            )}
            {metadata.resolution && (
              <div className="bg-slate-800/50 rounded-lg p-3">
                <p className="text-xs text-slate-400">Resolution</p>
                <p className="text-lg font-semibold">{metadata.resolution}</p>
              </div>
            )}
            {metadata.fps && (
              <div className="bg-slate-800/50 rounded-lg p-3">
                <p className="text-xs text-slate-400">FPS</p>
                <p className="text-lg font-semibold">{metadata.fps}</p>
              </div>
            )}
            {metadata.total_frames && (
              <div className="bg-slate-800/50 rounded-lg p-3">
                <p className="text-xs text-slate-400">Total Frames</p>
                <p className="text-lg font-semibold">{metadata.total_frames}</p>
              </div>
            )}
            {metadata.sample_rate && (
              <div className="bg-slate-800/50 rounded-lg p-3">
                <p className="text-xs text-slate-400">Sample Rate</p>
                <p className="text-lg font-semibold">{metadata.sample_rate} Hz</p>
              </div>
            )}
            {metadata.frames_analyzed != null && (
              <div className="bg-slate-800/50 rounded-lg p-3">
                <p className="text-xs text-slate-400">Frames Analyzed</p>
                <p className="text-lg font-semibold">{metadata.frames_analyzed}</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Temporal Analysis */}
      {report.temporal_analysis && (
        <div className="card p-6">
          <h3 className="text-lg font-semibold mb-4">Temporal Analysis</h3>
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-slate-800/50 rounded-lg p-3 text-center">
              <p className="text-xs text-slate-400">Temporal Consistency</p>
              <p className="text-2xl font-bold text-blue-400">{(report.temporal_analysis.temporal_consistency * 100).toFixed(1)}%</p>
            </div>
            <div className="bg-slate-800/50 rounded-lg p-3 text-center">
              <p className="text-xs text-slate-400">Flickering Score</p>
              <p className="text-2xl font-bold text-yellow-400">{(report.temporal_analysis.flickering_score * 100).toFixed(1)}%</p>
            </div>
            <div className="bg-slate-800/50 rounded-lg p-3 text-center">
              <p className="text-xs text-slate-400">Score Variance</p>
              <p className="text-2xl font-bold text-purple-400">{(report.temporal_analysis.score_variance * 100).toFixed(2)}%</p>
            </div>
          </div>
        </div>
      )}

      {/* Feature Analysis (Audio) */}
      {report.feature_analysis && (
        <div className="card p-6">
          <h3 className="text-lg font-semibold mb-4">Audio Feature Analysis</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {Object.entries(report.feature_analysis).map(([key, value]) => (
              <div key={key} className="bg-slate-800/50 rounded-lg p-3">
                <p className="text-xs text-slate-400">{key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</p>
                <div className="flex items-center gap-2 mt-1">
                  <div className="flex-1 bg-slate-700 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${value > 0.6 ? 'bg-green-500' : value > 0.3 ? 'bg-yellow-500' : 'bg-red-500'}`}
                      style={{ width: `${value * 100}%` }}
                    />
                  </div>
                  <span className="text-sm font-semibold">{(value * 100).toFixed(0)}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Link Analysis Details */}
      {report.analysis_type === 'link' && report.checks && (
        <div className="card p-6">
          <h3 className="text-lg font-semibold mb-4">Link Safety Checks</h3>
          <div className="space-y-3">
            {Object.entries(report.checks).map(([key, check]) => {
              const statusColors = {
                safe: 'bg-green-500/10 border-green-500/30 text-green-400',
                warning: 'bg-yellow-500/10 border-yellow-500/30 text-yellow-400',
                danger: 'bg-red-500/10 border-red-500/30 text-red-400',
                neutral: 'bg-slate-700/50 border-slate-600 text-slate-300',
                unknown: 'bg-slate-700/50 border-slate-600 text-slate-400',
              };
              const statusIcons = { safe: '✓', warning: '⚠', danger: '✗', neutral: '●', unknown: '?' };
              const colorClass = statusColors[check.status] || statusColors.unknown;
              return (
                <div key={key} className={`border rounded-lg p-4 ${colorClass}`}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="text-lg">{statusIcons[check.status] || '?'}</span>
                      <div>
                        <p className="font-medium">{key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</p>
                        <p className="text-sm opacity-80">{check.detail}</p>
                      </div>
                    </div>
                    <span className="text-lg font-bold">{check.score}%</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Verdict */}
      {report.verdict && (
        <div className={`card p-6 border ${
          report.risk_score >= 50 ? 'border-red-500/30 bg-red-500/5' : 'border-green-500/30 bg-green-500/5'
        }`}>
          <h3 className="text-lg font-semibold mb-2">Verdict</h3>
          <p className={`text-lg ${report.risk_score >= 50 ? 'text-red-400' : 'text-green-400'}`}>
            {report.verdict}
          </p>
          {report.risk_details && report.risk_details.length > 0 && (
            <div className="mt-4">
              <p className="text-sm text-slate-400 mb-2">Issues found:</p>
              <ul className="list-disc list-inside text-sm text-slate-300 space-y-1">
                {report.risk_details.map((detail, i) => (
                  <li key={i}>{detail}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Platform Info (YouTube etc.) */}
      {report.platform_info && report.platform_info.title && (
        <div className="card p-6">
          <h3 className="text-lg font-semibold mb-4">Platform Info — {report.platform_info.platform}</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div className="bg-slate-800/50 rounded-lg p-3">
              <p className="text-xs text-slate-400">Title</p>
              <p className="text-sm font-semibold">{report.platform_info.title}</p>
            </div>
            <div className="bg-slate-800/50 rounded-lg p-3">
              <p className="text-xs text-slate-400">Channel</p>
              <p className="text-sm font-semibold">
                {report.platform_info.channel}
                {report.platform_info.channel_verified && <span className="text-blue-400 ml-1">✓</span>}
              </p>
            </div>
            {report.platform_info.view_count > 0 && (
              <div className="bg-slate-800/50 rounded-lg p-3">
                <p className="text-xs text-slate-400">Views</p>
                <p className="text-sm font-semibold">{report.platform_info.view_count.toLocaleString()}</p>
              </div>
            )}
            {report.platform_info.like_count > 0 && (
              <div className="bg-slate-800/50 rounded-lg p-3">
                <p className="text-xs text-slate-400">Likes</p>
                <p className="text-sm font-semibold">{report.platform_info.like_count.toLocaleString()}</p>
              </div>
            )}
            {report.platform_info.channel_follower_count > 0 && (
              <div className="bg-slate-800/50 rounded-lg p-3">
                <p className="text-xs text-slate-400">Subscribers</p>
                <p className="text-sm font-semibold">{report.platform_info.channel_follower_count.toLocaleString()}</p>
              </div>
            )}
            {report.platform_info.upload_date && (
              <div className="bg-slate-800/50 rounded-lg p-3">
                <p className="text-xs text-slate-400">Upload Date</p>
                <p className="text-sm font-semibold">{report.platform_info.upload_date}</p>
              </div>
            )}
          </div>
          {report.platform_info.description_snippet && (
            <div className="mt-4 bg-slate-800/50 rounded-lg p-3">
              <p className="text-xs text-slate-400 mb-1">Description</p>
              <p className="text-sm text-slate-300">{report.platform_info.description_snippet}</p>
            </div>
          )}
        </div>
      )}

      {/* Segment Analysis (Audio) */}
      {report.segment_analysis && report.segment_analysis.length > 0 && (
        <div className="card p-6">
          <h3 className="text-lg font-semibold mb-4">
            Segment Analysis
            <span className="text-sm font-normal text-slate-400 ml-2">
              Consistency: {(report.segment_consistency * 100).toFixed(1)}%
            </span>
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-slate-400 border-b border-slate-700">
                  <th className="text-left py-2 px-3">Time Range</th>
                  <th className="text-left py-2 px-3">MFCC Mean</th>
                  <th className="text-left py-2 px-3">ZCR Mean</th>
                  <th className="text-left py-2 px-3">RMS Energy</th>
                </tr>
              </thead>
              <tbody>
                {report.segment_analysis.map((seg, i) => (
                  <tr key={i} className="border-b border-slate-700/50 hover:bg-slate-800/30">
                    <td className="py-2 px-3">{seg.start_time}s - {seg.end_time}s</td>
                    <td className="py-2 px-3">{seg.mfcc_mean.toFixed(4)}</td>
                    <td className="py-2 px-3">{seg.zcr_mean.toFixed(4)}</td>
                    <td className="py-2 px-3">{seg.rms_mean.toFixed(4)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
