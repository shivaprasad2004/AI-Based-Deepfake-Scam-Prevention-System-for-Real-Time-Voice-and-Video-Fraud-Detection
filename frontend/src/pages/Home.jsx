import { Link } from 'react-router-dom';
import { motion, useInView } from 'framer-motion';
import { useRef, useState, useEffect } from 'react';
import { FiShield, FiVideo, FiMic, FiLink, FiBarChart2, FiUploadCloud, FiArrowRight, FiCheck, FiZap, FiLock, FiGlobe } from 'react-icons/fi';

function AnimatedCounter({ target, suffix = '', duration = 2000 }) {
  const [count, setCount] = useState(0);
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true });

  useEffect(() => {
    if (!isInView) return;
    let start = 0;
    const step = target / (duration / 16);
    const timer = setInterval(() => {
      start += step;
      if (start >= target) { setCount(target); clearInterval(timer); }
      else setCount(Math.floor(start));
    }, 16);
    return () => clearInterval(timer);
  }, [isInView, target, duration]);

  return <span ref={ref}>{count.toLocaleString()}{suffix}</span>;
}

function FeatureCard({ icon: Icon, title, desc, delay, color }) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-50px' });
  const [tilt, setTilt] = useState({ x: 0, y: 0 });

  const handleMouse = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width - 0.5) * 15;
    const y = ((e.clientY - rect.top) / rect.height - 0.5) * -15;
    setTilt({ x, y });
  };

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 40 }}
      animate={isInView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.6, delay }}
      onMouseMove={handleMouse}
      onMouseLeave={() => setTilt({ x: 0, y: 0 })}
      style={{ transform: `perspective(800px) rotateY(${tilt.x}deg) rotateX(${tilt.y}deg)`, transition: 'transform 0.15s ease-out' }}
      className="card-glow p-6 group cursor-default"
    >
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-4 ${color} transition-transform duration-300 group-hover:scale-110`}>
        <Icon size={24} />
      </div>
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      <p className="text-slate-400 text-sm leading-relaxed">{desc}</p>
    </motion.div>
  );
}

function StepCard({ number, title, desc, delay, icon: Icon }) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-50px' });

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, x: -30 }}
      animate={isInView ? { opacity: 1, x: 0 } : {}}
      transition={{ duration: 0.5, delay }}
      className="flex gap-5 items-start"
    >
      <div className="relative flex-shrink-0">
        <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 border border-blue-500/20 flex items-center justify-center">
          <Icon size={24} className="text-blue-400" />
        </div>
        <div className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center text-xs font-bold">
          {number}
        </div>
      </div>
      <div>
        <h4 className="font-semibold text-lg mb-1">{title}</h4>
        <p className="text-slate-400 text-sm leading-relaxed">{desc}</p>
      </div>
    </motion.div>
  );
}

export default function Home() {
  return (
    <div className="relative grid-pattern">
      {/* Orbs */}
      <div className="orb orb-1" />
      <div className="orb orb-2" />
      <div className="orb orb-3" />

      {/* ===== Hero ===== */}
      <section className="relative min-h-[90vh] flex items-center justify-center px-4">
        <div className="max-w-5xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
          >
            {/* Badge */}
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-sm mb-8"
            >
              <FiZap size={14} />
              AI-Powered Deepfake Detection
            </motion.div>

            {/* Headline */}
            <h1 className="text-5xl md:text-7xl font-extrabold leading-tight mb-6">
              <span className="block">Detect</span>
              <span className="gradient-text block">Deepfakes & Scams</span>
              <span className="block">Instantly</span>
            </h1>

            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
              className="text-lg md:text-xl text-slate-400 max-w-2xl mx-auto mb-10"
            >
              Upload videos, audio, or paste any URL — our AI analyzes content
              in real-time to protect you from manipulated media and phishing links.
            </motion.p>

            {/* CTA Buttons */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.7 }}
              className="flex flex-col sm:flex-row gap-4 justify-center"
            >
              <Link to="/signup" className="btn-primary text-lg px-8 py-4 flex items-center justify-center gap-2 no-underline">
                Get Started Free <FiArrowRight />
              </Link>
              <Link to="/login" className="btn-secondary text-lg px-8 py-4 flex items-center justify-center gap-2 no-underline">
                Sign In
              </Link>
            </motion.div>
          </motion.div>

          {/* Floating icons */}
          <motion.div
            className="absolute top-20 right-10 hidden lg:block"
            animate={{ y: [0, -15, 0], rotate: [0, 5, 0] }}
            transition={{ duration: 5, repeat: Infinity, ease: 'easeInOut' }}
          >
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 border border-blue-500/20 flex items-center justify-center backdrop-blur-sm">
              <FiShield size={36} className="text-blue-400" />
            </div>
          </motion.div>

          <motion.div
            className="absolute bottom-32 left-10 hidden lg:block"
            animate={{ y: [0, 12, 0], rotate: [0, -5, 0] }}
            transition={{ duration: 6, repeat: Infinity, ease: 'easeInOut', delay: 1 }}
          >
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-500/20 to-pink-500/20 border border-purple-500/20 flex items-center justify-center backdrop-blur-sm">
              <FiLock size={28} className="text-purple-400" />
            </div>
          </motion.div>
        </div>
      </section>

      {/* Glow divider */}
      <div className="glow-line max-w-4xl mx-auto" />

      {/* ===== Stats ===== */}
      <section className="py-20 px-4">
        <div className="max-w-5xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-6">
          {[
            { label: 'Scans Performed', value: 15000, suffix: '+' },
            { label: 'Threats Detected', value: 4200, suffix: '+' },
            { label: 'Accuracy Rate', value: 98, suffix: '%' },
            { label: 'Links Analyzed', value: 8500, suffix: '+' },
          ].map((stat, i) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="text-center p-6 card"
            >
              <p className="text-3xl md:text-4xl font-bold gradient-text-blue">
                <AnimatedCounter target={stat.value} suffix={stat.suffix} />
              </p>
              <p className="text-slate-400 text-sm mt-2">{stat.label}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* ===== Features ===== */}
      <section className="py-20 px-4">
        <div className="max-w-5xl mx-auto">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-center mb-14"
          >
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Powerful <span className="gradient-text">Detection</span> Features
            </h2>
            <p className="text-slate-400 max-w-xl mx-auto">
              Multi-layered AI analysis to protect you from deepfakes, manipulated audio, and malicious links.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            <FeatureCard icon={FiVideo} title="Video Deepfake Detection" desc="EfficientNet AI model analyzes facial features, temporal consistency, and frame quality to detect manipulated videos." delay={0} color="bg-blue-500/15 text-blue-400" />
            <FeatureCard icon={FiMic} title="Audio Deepfake Detection" desc="Advanced spectral analysis with MFCC features, pitch detection, and segment consistency to spot synthetic audio." delay={0.1} color="bg-purple-500/15 text-purple-400" />
            <FeatureCard icon={FiGlobe} title="URL Link Checker" desc="Comprehensive URL analysis — domain trust, phishing detection, SSL verification, redirect chains, and more." delay={0.2} color="bg-pink-500/15 text-pink-400" />
            <FeatureCard icon={FiUploadCloud} title="Multiple Upload Options" desc="Upload files directly, paste YouTube/social media URLs, or use Google Drive links for seamless analysis." delay={0.3} color="bg-cyan-500/15 text-cyan-400" />
            <FeatureCard icon={FiBarChart2} title="Detailed Reports" desc="Visual charts, risk scores, confidence levels, and frame-by-frame analysis in comprehensive reports." delay={0.4} color="bg-amber-500/15 text-amber-400" />
            <FeatureCard icon={FiShield} title="Real-time Protection" desc="Get instant verdicts with risk levels — Low, Medium, High, or Critical — to make informed decisions." delay={0.5} color="bg-green-500/15 text-green-400" />
          </div>
        </div>
      </section>

      <div className="glow-line max-w-4xl mx-auto" />

      {/* ===== How It Works ===== */}
      <section className="py-20 px-4">
        <div className="max-w-3xl mx-auto">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-center mb-14"
          >
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              How It <span className="gradient-text">Works</span>
            </h2>
            <p className="text-slate-400">Three simple steps to verify any content</p>
          </motion.div>

          <div className="space-y-10">
            <StepCard number={1} icon={FiUploadCloud} title="Upload or Paste Link" desc="Drag & drop a video/audio file, paste a YouTube URL, or enter any suspicious link to check." delay={0} />
            <StepCard number={2} icon={FiZap} title="AI Analysis" desc="Our AI engine runs deepfake detection models, spectral analysis, and URL safety checks in real-time." delay={0.15} />
            <StepCard number={3} icon={FiCheck} title="Get Your Report" desc="Receive a detailed report with risk score, confidence level, visual charts, and a clear verdict." delay={0.3} />
          </div>
        </div>
      </section>

      <div className="glow-line max-w-4xl mx-auto" />

      {/* ===== CTA ===== */}
      <section className="py-24 px-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          className="max-w-3xl mx-auto text-center relative"
        >
          <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 via-purple-500/10 to-pink-500/10 rounded-3xl blur-2xl" />
          <div className="relative card p-12 md:p-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Ready to <span className="gradient-text">Protect</span> Yourself?
            </h2>
            <p className="text-slate-400 mb-8 max-w-md mx-auto">
              Start detecting deepfakes and verifying links in seconds. Free to use, no credit card required.
            </p>
            <Link to="/signup" className="btn-primary text-lg px-10 py-4 inline-flex items-center gap-2 no-underline">
              Start Scanning Now <FiArrowRight />
            </Link>
          </div>
        </motion.div>
      </section>

      {/* Footer */}
      <footer className="py-8 text-center text-slate-500 text-sm border-t border-slate-800/50">
        <p>&copy; {new Date().getFullYear()} DeepGuard AI. Built for safety.</p>
      </footer>
    </div>
  );
}
