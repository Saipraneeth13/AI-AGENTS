export default function Card({ title, subtitle, children, className = '', headerAction = null }) {
  return (
    <section className={`rounded-[28px] border border-slate-700/80 bg-slate-950/90 shadow-[0_30px_80px_rgba(15,23,42,0.35)] p-6 backdrop-blur-xl ${className}`}>
      {(title || subtitle || headerAction) && (
        <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div>
            {title && <h2 className="text-2xl font-semibold text-slate-100">{title}</h2>}
            {subtitle && <p className="mt-2 text-sm text-slate-400 max-w-2xl">{subtitle}</p>}
          </div>
          {headerAction}
        </div>
      )}
      {children}
    </section>
  );
}
