export default function ResultCard({ scan }) {
  if (!scan) return null;

  const fakePercent = scan.fake_percentage;
  const realPercent = scan.real_percentage;
  const circumference = 2 * Math.PI * 45;
  const offset = circumference - (fakePercent / 100) * circumference;

  const riskColors = {
    Critical: { stroke: '#ef4444', bg: 'bg-red-500/10', text: 'text-red-400', border: 'border-red-500/30' },
    High: { stroke: '#f97316', bg: 'bg-orange-500/10', text: 'text-orange-400', border: 'border-orange-500/30' },
    Medium: { stroke: '#eab308', bg: 'bg-yellow-500/10', text: 'text-yellow-400', border: 'border-yellow-500/30' },
    Low: { stroke: '#22c55e', bg: 'bg-green-500/10', text: 'text-green-400', border: 'border-green-500/30' },
  };

  const colors = riskColors[scan.risk_level] || riskColors.Low;

  return (
    <div className={`card p-6 border ${colors.border}`}>
      <div className="flex flex-col md:flex-row items-center gap-8">
        {/* Gauge */}
        <div className="relative">
          <svg width="160" height="160" viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="45" fill="none" stroke="#334155" strokeWidth="8" />
            <circle
              cx="50" cy="50" r="45" fill="none"
              stroke={colors.stroke}
              strokeWidth="8"
              strokeDasharray={circumference}
              strokeDashoffset={offset}
              strokeLinecap="round"
              transform="rotate(-90 50 50)"
              className="gauge-circle"
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className={`text-3xl font-bold ${colors.text}`}>{fakePercent}%</span>
            <span className="text-xs text-slate-400">Fake</span>
          </div>
        </div>

        {/* Info */}
        <div className="flex-1 space-y-4">
          <div>
            <h3 className="text-lg font-semibold mb-1">{scan.filename}</h3>
            <span className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${colors.bg} ${colors.text}`}>
              {scan.risk_level} Risk
            </span>
            <span className="inline-block px-3 py-1 rounded-full text-xs font-semibold bg-slate-700 text-slate-300 ml-2">
              {scan.file_type === 'video' ? 'Video' : scan.file_type === 'audio' ? 'Audio' : 'Link'}
            </span>
          </div>

          <div className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <span className="text-slate-400">Real:</span>
              <span className="ml-2 text-green-400 font-semibold">{realPercent}%</span>
            </div>
            <div>
              <span className="text-slate-400">Confidence:</span>
              <span className="ml-2 text-blue-400 font-semibold">{scan.confidence_score}%</span>
            </div>
            {scan.duration && (
              <div>
                <span className="text-slate-400">Duration:</span>
                <span className="ml-2">{scan.duration}s</span>
              </div>
            )}
            {scan.resolution && (
              <div>
                <span className="text-slate-400">Resolution:</span>
                <span className="ml-2">{scan.resolution}</span>
              </div>
            )}
          </div>

          {/* Fake/Real bar */}
          <div>
            <div className="flex justify-between text-xs text-slate-400 mb-1">
              <span>Real {realPercent}%</span>
              <span>Fake {fakePercent}%</span>
            </div>
            <div className="w-full h-3 bg-slate-700 rounded-full overflow-hidden flex">
              <div className="bg-green-500 h-full transition-all" style={{ width: `${realPercent}%` }} />
              <div className="bg-red-500 h-full transition-all" style={{ width: `${fakePercent}%` }} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
