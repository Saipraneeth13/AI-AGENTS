import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Upload, BarChart3, Home, Sparkles } from 'lucide-react';
import UploadPage from './pages/UploadPage';
import AssessmentPage from './pages/AssessmentPage';
import DashboardPage from './pages/DashboardPage';

const navItems = [
  { path: '/', label: 'Upload', icon: Upload },
  { path: '/assessment', label: 'Assessment', icon: BarChart3 },
  { path: '/dashboard', label: 'Dashboard', icon: Home },
];

function Navigation() {
  const location = useLocation();

  return (
    <nav className="flex flex-wrap items-center gap-3">
      {navItems.map(({ path, label, icon: Icon }) => {
        const isActive = location.pathname === path || location.pathname.startsWith(`${path}/`);
        return (
          <Link
            key={label}
            to={path}
            className={`inline-flex items-center gap-2 rounded-2xl px-4 py-2 text-sm font-medium transition duration-300 ${
              isActive
                ? 'bg-amber-500/14 text-amber-300 shadow-sm shadow-amber-500/20'
                : 'text-slate-300 hover:bg-slate-800/80 hover:text-slate-100'
            }`}
          >
            <Icon size={18} />
            <span>{label}</span>
          </Link>
        );
      })}
    </nav>
  );
}

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-950 text-slate-100">
        <div className="pointer-events-none absolute inset-0 overflow-hidden opacity-10">
          <div className="absolute top-16 left-8 h-72 w-72 rounded-full bg-amber-500 blur-3xl" />
          <div className="absolute bottom-12 right-12 h-80 w-80 rounded-full bg-sky-400 blur-3xl" />
        </div>

        <header className="relative z-10 border-b border-slate-800/75 bg-slate-950/95 backdrop-blur-xl">
          <div className="mx-auto flex max-w-7xl flex-col gap-4 px-6 py-5 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-3xl bg-gradient-to-br from-amber-400 to-amber-600 shadow-[0_24px_60px_rgba(245,158,11,0.18)]">
                <Sparkles size={22} className="text-white" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-white sm:text-2xl">SkillSense</h1>
                <p className="text-sm text-slate-400">Modern AI assessment for real-world career growth.</p>
              </div>
            </div>
            <Navigation />
          </div>
        </header>

        <main className="relative z-10 mx-auto flex min-h-[calc(100vh-220px)] max-w-7xl flex-col px-4 py-8 sm:px-6 lg:px-8">
          <Routes>
            <Route path="/" element={<UploadPage />} />
            <Route path="/assessment" element={<AssessmentPage />} />
            <Route path="/assessment/:sessionId" element={<AssessmentPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/dashboard/:sessionId" element={<DashboardPage />} />
          </Routes>
        </main>

        <footer className="relative z-10 border-t border-slate-800/75 bg-slate-950/90 backdrop-blur-xl">
          <div className="mx-auto max-w-7xl px-6 py-5 text-center text-sm text-slate-500 sm:px-8">
            © 2026 SkillSense · Designed for clarity, performance, and accessibility.
          </div>
        </footer>
      </div>
    </BrowserRouter>
  );
}

export default App;
