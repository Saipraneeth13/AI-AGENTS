import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { UploadCloud, FileText, ChevronRight, Sparkles, Target } from 'lucide-react';
import Button from '../components/ui/Button';
import Card from '../components/ui/Card';
import SectionHeader from '../components/ui/SectionHeader';

export default function UploadPage() {
  const [resume, setResume] = useState(null);
  const [jd, setJd] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const resumeLabel = resume ? resume.name : 'Drag and drop a PDF or click to upload';

  const handleFileChange = (event) => {
    const file = event.target.files?.[0] ?? null;
    setResume(file);
    setError('');
  };

  const handleStart = () => {
    if (!resume) {
      setError('Please upload your resume to continue.');
      return;
    }

    setError('');
    setIsSubmitting(true);

    setTimeout(() => {
      setIsSubmitting(false);
      navigate('/assessment/test-session-123');
    }, 1400);
  };

  return (
    <div className="flex min-h-full flex-col gap-8 animate-fade-in-up">
      <SectionHeader
        eyebrow="Resume assessment"
        title="Launch your personalized skill review"
        description="Upload your resume and target job description to get a tailored assessment, gap analysis, and next-step learning plan."
      />

      <div className="grid gap-8 xl:grid-cols-[1.2fr_0.8fr]">
        <Card className="space-y-8">
          <div className="grid gap-6 sm:grid-cols-2">
            <div className="space-y-4 rounded-3xl bg-slate-900/95 p-6 shadow-[0_24px_45px_rgba(15,23,42,0.25)] border border-slate-800">
              <div className="flex items-center gap-3">
                <div className="flex h-12 w-12 items-center justify-center rounded-3xl bg-slate-800 text-amber-300 shadow-lg shadow-amber-500/10">
                  <FileText size={20} />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-slate-100">Upload resume</h3>
                  <p className="text-sm text-slate-400">Accepted format: PDF only</p>
                </div>
              </div>
              <label
                htmlFor="resume-upload"
                className="group flex min-h-[220px] flex-col items-center justify-center rounded-3xl border border-dashed border-slate-700/90 bg-slate-950/60 px-6 text-center transition hover:border-amber-400/50 hover:bg-slate-900/80"
              >
                <input
                  id="resume-upload"
                  type="file"
                  accept=".pdf"
                  onChange={handleFileChange}
                  className="sr-only"
                  aria-describedby="resume-upload-help"
                />
                <UploadCloud className="mb-4 h-12 w-12 text-amber-400 transition group-hover:text-amber-300" />
                <div>
                  <p className="text-lg font-medium text-slate-100">{resumeLabel}</p>
                  <p id="resume-upload-help" className="mt-2 text-sm text-slate-500">
                    Upload your resume to start the analysis.
                  </p>
                </div>
              </label>
            </div>

            <div className="space-y-4 rounded-3xl bg-slate-900/95 p-6 shadow-[0_24px_45px_rgba(15,23,42,0.25)] border border-slate-800">
              <div className="flex items-center gap-3">
                <div className="flex h-12 w-12 items-center justify-center rounded-3xl bg-slate-800 text-sky-400 shadow-lg shadow-sky-500/10">
                  <Target size={20} />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-slate-100">Job description</h3>
                  <p className="text-sm text-slate-400">Paste the posting for a precise alignment review.</p>
                </div>
              </div>
              <textarea
                value={jd}
                onChange={(event) => setJd(event.target.value)}
                rows={10}
                placeholder="Paste the job description here..."
                className="w-full resize-none rounded-3xl border border-slate-700/80 bg-slate-950/80 p-5 text-sm text-slate-100 outline-none transition focus:border-sky-400 focus:ring-2 focus:ring-sky-400/20"
              />
            </div>
          </div>

          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="text-sm text-slate-400">
              Need more accurate results? Add a detailed job description and keep your resume PDF clean and concise.
            </div>
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
              <Button
                onClick={handleStart}
                disabled={isSubmitting}
                aria-label="Start assessment"
                className="min-w-[190px]"
              >
                {isSubmitting ? (
                  <span className="inline-flex items-center gap-2">
                    <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/50 border-t-transparent" />
                    Analyzing...
                  </span>
                ) : (
                  <>
                    <span>Start assessment</span>
                    <ChevronRight size={18} />
                  </>
                )}
              </Button>
              {error && <p className="text-sm text-rose-400">{error}</p>}
            </div>
          </div>
        </Card>

        <Card title="How it works" subtitle="Upload once and get a full skills report with clear next steps.">
          <div className="grid gap-4 sm:grid-cols-2">
            {[
              { title: 'Smart parsing', description: 'Automatic analysis of your resume and job description to identify strengths and gaps.' },
              { title: 'Clear recommendations', description: 'Actionable learning steps that help you improve where it matters most.' },
            ].map((item) => (
              <div key={item.title} className="rounded-3xl border border-slate-800/80 bg-slate-950/70 p-5">
                <h4 className="text-lg font-semibold text-slate-100">{item.title}</h4>
                <p className="mt-2 text-sm text-slate-400">{item.description}</p>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
