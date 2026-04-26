export default function SectionHeader({ eyebrow, title, description, icon }) {
  return (
    <header className="space-y-3">
      {eyebrow && <p className="text-sm uppercase tracking-[0.3em] text-amber-400/80">{eyebrow}</p>}
      {title && <h1 className="text-4xl font-semibold tracking-tight text-slate-100 sm:text-5xl">{title}</h1>}
      {description && <p className="max-w-3xl text-base leading-7 text-slate-400">{description}</p>}
      {icon && <div className="text-amber-400">{icon}</div>}
    </header>
  );
}
