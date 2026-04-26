import { useParams } from 'react-router-dom';
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';
import { BookOpen, Target, AlertCircle } from 'lucide-react';
import Card from '../components/ui/Card';
import SectionHeader from '../components/ui/SectionHeader';

const mockSkills = [
  { subject: 'Python', A: 85, fullMark: 100 },
  { subject: 'React', A: 65, fullMark: 100 },
  { subject: 'System Design', A: 50, fullMark: 100 },
  { subject: 'Communication', A: 90, fullMark: 100 },
  { subject: 'Problem Solving', A: 75, fullMark: 100 },
];

const growthPlan = [
  {
    title: 'Week 1: System Design Fundamentals',
    description:
      'Focus on architecture, scalability, and reliability. Use diagrams and prototypes to support your answers in interviews.',
    color: 'emerald',
    actions: ['Read core system design patterns', 'Build a caching architecture', 'Review distributed systems fundamentals'],
  },
  {
    title: 'Week 2: React & Delivery',
    description:
      'Improve frontend performance, state management, and component design for faster iteration and cleaner code.',
    color: 'sky',
    actions: ['Practice hooks and memoization', 'Refactor a component using custom hooks', 'Review application architecture'],
  },
];

export default function DashboardPage() {
  const { sessionId } = useParams();

  return (
    <div className="space-y-8">
      <SectionHeader
        eyebrow="Session results"
        title="Your assessment dashboard"
        description="A concise view of your skills, gaps, and recommended next steps. Use this to guide your upskilling plan and interview prep."
      />

      <div className="grid gap-6 xl:grid-cols-[1.25fr_0.75fr]">
        <Card title="Performance summary" subtitle="Visualize your skill strengths and potential opportunity areas.">
          <div className="grid gap-4 sm:grid-cols-2">
            {[
              { label: 'Session', value: sessionId ?? 'Pending', icon: Target, tone: 'text-sky-400' },
              { label: 'Primary focus', value: 'System design', icon: AlertCircle, tone: 'text-rose-400' },
            ].map((item) => (
              <div key={item.label} className="rounded-3xl border border-slate-800/90 bg-slate-950/80 p-5">
                <div className="flex items-center gap-3 text-sm text-slate-400">
                  <item.icon size={18} className={`${item.tone}`} />
                  <span>{item.label}</span>
                </div>
                <p className="mt-4 text-2xl font-semibold text-slate-100">{item.value}</p>
              </div>
            ))}
          </div>
        </Card>

        <Card title="Key metrics" subtitle="Your current skill scores and where to improve.">
          <div className="grid gap-4 sm:grid-cols-2">
            {mockSkills.slice(0, 4).map((skill) => (
              <div key={skill.subject} className="rounded-3xl border border-slate-800/90 bg-slate-950/80 p-5">
                <div className="flex items-center justify-between gap-4">
                  <p className="font-medium text-slate-200">{skill.subject}</p>
                  <span className="rounded-full bg-slate-800 px-3 py-1 text-xs uppercase tracking-[0.18em] text-slate-400">
                    {skill.A}%
                  </span>
                </div>
                <div className="mt-4 h-2 overflow-hidden rounded-full bg-slate-800">
                  <div className="h-full rounded-full bg-gradient-to-r from-amber-500 to-sky-500" style={{ width: `${skill.A}%` }} />
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <Card title="Skill radar" subtitle="A quick visual map of your current capabilities.">
          <div className="h-[360px]">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={mockSkills}> 
                <PolarGrid stroke="#334155" />
                <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                <Radar dataKey="A" stroke="#60a5fa" fill="#60a5fa" fillOpacity={0.32} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card title="Gap analysis" subtitle="Identify the top areas to focus on for your next months." headerAction={null}>
          <div className="h-[360px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                layout="vertical"
                data={mockSkills}
                margin={{ top: 8, right: 12, left: 0, bottom: 8 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis type="number" domain={[0, 100]} tick={{ fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                <YAxis dataKey="subject" type="category" tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} width={120} />
                <Tooltip
                  cursor={{ fill: 'rgba(30,41,59,0.7)' }}
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    border: '1px solid rgba(148,163,184,0.12)',
                    borderRadius: '14px',
                    color: '#e2e8f0',
                  }}
                />
                <Bar dataKey="A" fill="#8b5cf6" radius={[0, 8, 8, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      <Card title="Personalized learning plan" subtitle="A practical guide for your next two weeks of improvement.">
        <div className="grid gap-4">
          {growthPlan.map((plan) => (
            <article key={plan.title} className="rounded-3xl border border-slate-800/90 bg-slate-950/80 p-6">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <h4 className="text-xl font-semibold text-slate-100">{plan.title}</h4>
                  <p className="mt-2 text-sm text-slate-400">{plan.description}</p>
                </div>
                <span
                  className={`rounded-2xl px-3 py-1 text-xs uppercase tracking-[0.2em] ${
                    plan.color === 'emerald'
                      ? 'border border-emerald-500/20 bg-emerald-400/10 text-emerald-300'
                      : 'border border-sky-500/20 bg-sky-400/10 text-sky-300'
                  }`}
                >
                  Recommended
                </span>
              </div>
              <ul className="mt-5 grid gap-3 text-slate-300 sm:grid-cols-2">
                {plan.actions.map((item) => (
                  <li key={item} className="rounded-2xl border border-slate-800/80 bg-slate-900/90 p-4 text-sm">{item}</li>
                ))}
              </ul>
            </article>
          ))}
        </div>
      </Card>
    </div>
  );
}
