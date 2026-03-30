function LoadingSkeleton() {
  return (
    <div className="space-y-6 animate-fade-in">
      {/* Status message */}
      <div className="text-center space-y-2">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-brand-500/10 border border-brand-500/20">
          <span className="w-2 h-2 rounded-full bg-brand-400 animate-pulse" />
          <span className="text-sm text-brand-300 font-medium">Interpreting your data...</span>
        </div>
      </div>

      {/* Toggle skeleton */}
      <div className="flex items-center justify-between">
        <div className="shimmer-bg h-10 w-52 rounded-full" />
        <div className="flex gap-2">
          <div className="shimmer-bg h-10 w-16 rounded-xl" />
          <div className="shimmer-bg h-10 w-18 rounded-xl" />
        </div>
      </div>

      {/* Narrative skeleton */}
      <div className="card p-8 space-y-4">
        <div className="shimmer-bg h-5 rounded-lg w-full" />
        <div className="shimmer-bg h-5 rounded-lg w-11/12" />
        <div className="shimmer-bg h-5 rounded-lg w-4/5" />
        <div className="shimmer-bg h-5 rounded-lg w-9/12" />
      </div>

      {/* Signal cards skeleton */}
      <div className="grid grid-cols-3 gap-4">
        {[0, 1, 2].map((i) => (
          <div key={i} className="card p-5 space-y-3">
            <div className="shimmer-bg h-3 rounded w-20" />
            <div className="shimmer-bg h-7 rounded w-24" />
          </div>
        ))}
      </div>

      {/* Flags skeleton */}
      <div className="grid grid-cols-2 gap-4">
        <div className="card p-5 space-y-2">
          <div className="shimmer-bg h-3 rounded w-12" />
          <div className="shimmer-bg h-4 rounded w-full" />
          <div className="shimmer-bg h-4 rounded w-3/4" />
        </div>
        <div className="card p-5 space-y-2">
          <div className="shimmer-bg h-3 rounded w-20" />
          <div className="shimmer-bg h-4 rounded w-full" />
          <div className="shimmer-bg h-4 rounded w-3/4" />
        </div>
      </div>
    </div>
  );
}

export default LoadingSkeleton;
