import { useState, useCallback, useEffect, useRef } from 'react';
import { useDropzone } from 'react-dropzone';
import { FiUploadCloud, FiLink, FiHardDrive, FiFile, FiLoader, FiShield } from 'react-icons/fi';
import { uploadAPI } from '../services/api';

export default function UploadZone({ onResult, onError }) {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [activeTab, setActiveTab] = useState('local');
  const [url, setUrl] = useState('');
  const [driveUrl, setDriveUrl] = useState('');
  const [linkUrl, setLinkUrl] = useState('');
  const [statusMsg, setStatusMsg] = useState('');
  const [elapsedTime, setElapsedTime] = useState(0);
  const timerRef = useRef(null);

  // Timer for showing elapsed time during long operations
  useEffect(() => {
    if (uploading) {
      setElapsedTime(0);
      timerRef.current = setInterval(() => {
        setElapsedTime((t) => t + 1);
      }, 1000);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
    }
    return () => { if (timerRef.current) clearInterval(timerRef.current); };
  }, [uploading]);

  const formatTime = (seconds) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return m > 0 ? `${m}m ${s}s` : `${s}s`;
  };

  const handleAnalysis = async (apiCall, source) => {
    setUploading(true);
    setProgress(0);
    setStatusMsg(source === 'local' ? 'Uploading file...' : 'Downloading & analyzing... this may take 1-2 minutes');
    onError('');
    try {
      const res = await apiCall();
      setStatusMsg('Analysis complete!');
      onResult(res.data);
    } catch (err) {
      const msg = err.response?.data?.error
        || (err.code === 'ECONNABORTED' ? 'Request timed out. The video may be too large.' : '')
        || err.message
        || 'Analysis failed. Please try again.';
      onError(msg);
    } finally {
      setUploading(false);
      setProgress(0);
      setStatusMsg('');
    }
  };

  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length === 0) return;
    const file = acceptedFiles[0];
    handleAnalysis(() =>
      uploadAPI.local(file, (e) => {
        const pct = Math.round((e.loaded * 100) / e.total);
        setProgress(pct);
        if (pct >= 100) setStatusMsg('Analyzing file...');
      }),
      'local'
    );
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'video/*': ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv'],
      'audio/*': ['.mp3', '.wav', '.ogg', '.flac', '.aac', '.m4a'],
    },
    maxFiles: 1,
    disabled: uploading,
  });

  const handleUrlSubmit = (e) => {
    e.preventDefault();
    if (!url.trim()) return;
    handleAnalysis(() => uploadAPI.url(url.trim()), 'url');
  };

  const handleDriveSubmit = (e) => {
    e.preventDefault();
    if (!driveUrl.trim()) return;
    handleAnalysis(() => uploadAPI.drive(driveUrl.trim()), 'drive');
  };

  const handleLinkSubmit = (e) => {
    e.preventDefault();
    if (!linkUrl.trim()) return;
    handleAnalysis(() => uploadAPI.analyzeLink(linkUrl.trim()), 'link');
  };

  const tabs = [
    { id: 'local', label: 'Local Upload', icon: FiFile },
    { id: 'url', label: 'URL / YouTube', icon: FiLink },
    { id: 'drive', label: 'Google Drive', icon: FiHardDrive },
    { id: 'link', label: 'Link Check', icon: FiShield },
  ];

  return (
    <div className="card p-6">
      <h2 className="text-xl font-semibold mb-4">Upload Media for Analysis</h2>

      {/* Tabs */}
      <div className="flex gap-2 mb-6">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => !uploading && setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition border-0 cursor-pointer ${
              activeTab === tab.id
                ? 'bg-blue-600 text-white'
                : 'bg-slate-700/50 text-slate-300 hover:bg-slate-700'
            } ${uploading ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            <tab.icon size={16} /> {tab.label}
          </button>
        ))}
      </div>

      {/* Local Upload */}
      {activeTab === 'local' && !uploading && (
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition ${
            isDragActive
              ? 'border-blue-500 bg-blue-500/10'
              : 'border-slate-600 hover:border-blue-500/50'
          }`}
        >
          <input {...getInputProps()} />
          <FiUploadCloud className="mx-auto text-blue-400 mb-4" size={48} />
          {isDragActive ? (
            <p className="text-blue-400 text-lg">Drop the file here...</p>
          ) : (
            <>
              <p className="text-lg mb-2">Drag & drop your video or audio file here</p>
              <p className="text-slate-400 text-sm">or click to browse files</p>
              <p className="text-slate-500 text-xs mt-2">
                Supports: MP4, AVI, MOV, MKV, WebM, MP3, WAV, OGG, FLAC (Max 500MB)
              </p>
            </>
          )}
        </div>
      )}

      {/* URL Upload */}
      {activeTab === 'url' && !uploading && (
        <form onSubmit={handleUrlSubmit} className="space-y-4">
          <div>
            <label className="block text-sm text-slate-400 mb-2">
              Paste any video/audio URL (YouTube, Vimeo, Facebook, direct links, etc.)
            </label>
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://www.youtube.com/watch?v=... or any video URL"
              className="w-full bg-slate-800 border border-slate-600 rounded-lg px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
            />
            <p className="text-slate-500 text-xs mt-2">
              Supported: YouTube, Vimeo, Facebook, Instagram, Twitter/X, TikTok, Dailymotion, Reddit, or any direct video/audio link
            </p>
          </div>
          <button type="submit" className="btn-primary" disabled={!url.trim()}>
            Analyze from URL
          </button>
        </form>
      )}

      {/* Google Drive */}
      {activeTab === 'drive' && !uploading && (
        <form onSubmit={handleDriveSubmit} className="space-y-4">
          <div>
            <label className="block text-sm text-slate-400 mb-2">Google Drive sharing link</label>
            <input
              type="url"
              value={driveUrl}
              onChange={(e) => setDriveUrl(e.target.value)}
              placeholder="https://drive.google.com/file/d/..."
              className="w-full bg-slate-800 border border-slate-600 rounded-lg px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
            />
            <p className="text-slate-500 text-xs mt-1">Make sure the file sharing is set to "Anyone with the link"</p>
          </div>
          <button type="submit" className="btn-primary" disabled={!driveUrl.trim()}>
            Analyze from Drive
          </button>
        </form>
      )}

      {/* Link Check */}
      {activeTab === 'link' && !uploading && (
        <form onSubmit={handleLinkSubmit} className="space-y-4">
          <div>
            <label className="block text-sm text-slate-400 mb-2">
              Paste any URL to check if it's fake, phishing, or legitimate
            </label>
            <input
              type="url"
              value={linkUrl}
              onChange={(e) => setLinkUrl(e.target.value)}
              placeholder="https://example.com/suspicious-link..."
              className="w-full bg-slate-800 border border-slate-600 rounded-lg px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
            />
            <p className="text-slate-500 text-xs mt-2">
              Analyzes domain trust, SSL, phishing keywords, redirects, URL structure, and more
            </p>
          </div>
          <button type="submit" className="btn-primary" disabled={!linkUrl.trim()}>
            <FiShield className="inline mr-2" />
            Check Link Safety
          </button>
        </form>
      )}

      {/* Loading / Progress State */}
      {uploading && (
        <div className="border-2 border-blue-500/30 bg-blue-500/5 rounded-xl p-8 text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-blue-500/10 mb-4">
            <FiLoader className="text-blue-400 animate-spin" size={32} />
          </div>
          <p className="text-lg font-semibold text-blue-300 mb-2">{statusMsg}</p>
          <p className="text-slate-400 text-sm mb-4">
            Elapsed: {formatTime(elapsedTime)}
            {activeTab === 'url' && elapsedTime < 10 && (
              <span className="block mt-1 text-xs text-slate-500">
                Downloading video from URL, then running AI analysis...
              </span>
            )}
          </p>

          {/* Progress bar */}
          <div className="w-full max-w-md mx-auto bg-slate-700 rounded-full h-2.5">
            {progress > 0 ? (
              <div
                className="bg-gradient-to-r from-blue-500 to-purple-500 h-2.5 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            ) : (
              <div className="bg-gradient-to-r from-blue-500 to-purple-500 h-2.5 rounded-full animate-pulse w-2/3" />
            )}
          </div>
          {progress > 0 && (
            <p className="text-xs text-slate-500 mt-2">Upload: {progress}%</p>
          )}

          {/* Step indicators for URL */}
          {activeTab !== 'local' && (
            <div className="flex justify-center gap-8 mt-6 text-xs">
              <div className={`flex items-center gap-1 ${elapsedTime >= 0 ? 'text-blue-400' : 'text-slate-600'}`}>
                <span className="w-2 h-2 rounded-full bg-blue-400 inline-block" />
                Downloading
              </div>
              <div className={`flex items-center gap-1 ${elapsedTime >= 15 ? 'text-blue-400' : 'text-slate-600'}`}>
                <span className={`w-2 h-2 rounded-full inline-block ${elapsedTime >= 15 ? 'bg-blue-400' : 'bg-slate-600'}`} />
                Extracting frames
              </div>
              <div className={`flex items-center gap-1 ${elapsedTime >= 30 ? 'text-blue-400' : 'text-slate-600'}`}>
                <span className={`w-2 h-2 rounded-full inline-block ${elapsedTime >= 30 ? 'bg-blue-400' : 'bg-slate-600'}`} />
                AI Analysis
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
