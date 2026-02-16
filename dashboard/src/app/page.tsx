'use client';

import { useEffect, useState } from 'react';
import {
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import {
  getOverview, getCostAnalytics, getLatencyAnalytics, getUsageAnalytics, getErrorAnalytics, getTraces,
  OverviewData, CostData, LatencyData, UsageData, ErrorData, TraceListData
} from '@/lib/api';

// ── Color Palette ────────────────────────────────────────
const COLORS = ['#6366f1', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ec4899'];
const MODEL_COLORS: Record<string, string> = {
  'gpt-4o': '#6366f1',
  'gpt-4o-mini': '#8b5cf6',
  'gpt-3.5-turbo': '#06b6d4',
  'claude-3.5-sonnet': '#f59e0b',
  'claude-3-haiku': '#10b981',
};

// ── Nav Items ────────────────────────────────────────────
const NAV_ITEMS = [
  { key: 'overview', label: 'Overview', icon: '📊' },
  { key: 'cost', label: 'Cost Analytics', icon: '💰' },
  { key: 'performance', label: 'Performance', icon: '⚡' },
  { key: 'traces', label: 'Trace Explorer', icon: '🔍' },
  { key: 'errors', label: 'Errors', icon: '🚨' },
  { key: 'cache', label: 'Cache & Savings', icon: '💎' },
];

// ── Custom Tooltip ───────────────────────────────────────
function CustomTooltip({ active, payload, label }: { active?: boolean; payload?: Array<{ name: string; value: number; color: string }>; label?: string }) {
  if (!active || !payload) return null;
  return (
    <div style={{
      background: 'rgba(26,26,46,0.95)',
      border: '1px solid #2a2a4a',
      borderRadius: 12,
      padding: '12px 16px',
      boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
    }}>
      <p style={{ color: '#9898b0', fontSize: '0.75rem', marginBottom: 6 }}>{label}</p>
      {payload.map((p, i) => (
        <p key={i} style={{ color: p.color, fontSize: '0.875rem', fontWeight: 600 }}>
          {p.name}: {typeof p.value === 'number' && p.name.toLowerCase().includes('cost')
            ? `$${p.value.toFixed(2)}`
            : typeof p.value === 'number' && p.name.toLowerCase().includes('latency')
              ? `${p.value.toFixed(0)}ms`
              : p.value?.toLocaleString?.() ?? p.value}
        </p>
      ))}
    </div>
  );
}

export default function Dashboard() {
  const [page, setPage] = useState('overview');
  const [overview, setOverview] = useState<OverviewData | null>(null);
  const [cost, setCost] = useState<CostData | null>(null);
  const [latency, setLatency] = useState<LatencyData | null>(null);
  const [usage, setUsage] = useState<UsageData | null>(null);
  const [errors, setErrors] = useState<ErrorData | null>(null);
  const [traces, setTraces] = useState<TraceListData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      const [ov, co, la, us, er, tr] = await Promise.all([
        getOverview(), getCostAnalytics(), getLatencyAnalytics(),
        getUsageAnalytics(), getErrorAnalytics(), getTraces(),
      ]);
      setOverview(ov); setCost(co); setLatency(la);
      setUsage(us); setErrors(er); setTraces(tr);
      setLoading(false);
    }
    loadData();
  }, []);

  if (loading) {
    return (
      <div style={{ display: 'flex', height: '100vh', alignItems: 'center', justifyContent: 'center', background: '#0a0a0f' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '3rem', marginBottom: 16, animation: 'pulse 2s infinite' }}>🔮</div>
          <p style={{ color: '#9898b0', fontSize: '0.9rem' }}>Loading analytics...</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: '#0a0a0f' }}>
      {/* ── Sidebar ── */}
      <aside style={{
        width: 240,
        background: 'rgba(18,18,26,0.95)',
        borderRight: '1px solid #2a2a4a',
        padding: '24px 12px',
        display: 'flex',
        flexDirection: 'column',
        position: 'fixed',
        height: '100vh',
        zIndex: 10,
      }}>
        {/* Logo */}
        <div style={{ padding: '0 16px', marginBottom: 32 }}>
          <h1 style={{
            fontSize: '1.3rem',
            fontWeight: 800,
            background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            letterSpacing: '-0.02em',
          }}>
            ✦ PromptOps
          </h1>
          <p style={{ fontSize: '0.7rem', color: '#6a6a88', marginTop: 4 }}>LLM Observability</p>
        </div>

        {/* Nav */}
        <nav style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
          {NAV_ITEMS.map(item => (
            <button
              key={item.key}
              onClick={() => setPage(item.key)}
              className={`nav-item ${page === item.key ? 'active' : ''}`}
              style={{ border: 'none', cursor: 'pointer', background: 'transparent', textAlign: 'left', width: '100%' }}
            >
              <span>{item.icon}</span>
              <span>{item.label}</span>
            </button>
          ))}
        </nav>

        {/* Bottom stats */}
        <div style={{ marginTop: 'auto', padding: '16px', borderTop: '1px solid #2a2a4a' }}>
          <div style={{ fontSize: '0.7rem', color: '#6a6a88', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 8 }}>Quick Stats</div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem' }}>
            <span style={{ color: '#9898b0' }}>Models</span>
            <span style={{ color: '#6366f1', fontWeight: 600 }}>{overview?.active_models?.length || 0}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginTop: 4 }}>
            <span style={{ color: '#9898b0' }}>Uptime</span>
            <span style={{ color: '#10b981', fontWeight: 600 }}>99.2%</span>
          </div>
        </div>
      </aside>

      {/* ── Main Content ── */}
      <main style={{ flex: 1, marginLeft: 240, padding: '32px 40px' }}>
        {page === 'overview' && overview && cost && latency && usage && (
          <OverviewPage overview={overview} cost={cost} latency={latency} usage={usage} />
        )}
        {page === 'cost' && cost && (
          <CostPage cost={cost} />
        )}
        {page === 'performance' && latency && (
          <PerformancePage latency={latency} />
        )}
        {page === 'traces' && traces && (
          <TracesPage traces={traces} />
        )}
        {page === 'errors' && errors && (
          <ErrorsPage errors={errors} />
        )}
        {page === 'cache' && overview && (
          <CachePage overview={overview} />
        )}
      </main>
    </div>
  );
}


// ═══════════════════════════════════════════════════════════
// ── OVERVIEW PAGE
// ═══════════════════════════════════════════════════════════

function OverviewPage({ overview, cost, latency, usage }: {
  overview: OverviewData; cost: CostData; latency: LatencyData; usage: UsageData;
}) {
  return (
    <div className="animate-fade-in">
      <div style={{ marginBottom: 32 }}>
        <h2 style={{ fontSize: '1.8rem', fontWeight: 700, letterSpacing: '-0.02em' }}>Dashboard Overview</h2>
        <p style={{ color: '#9898b0', marginTop: 4 }}>Real-time metrics for your LLM operations</p>
      </div>

      {/* Metric Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 32 }}>
        <MetricCard label="Total Requests" value={overview.total_requests.toLocaleString()} icon="📡" accent="#6366f1" />
        <MetricCard label="Total Cost" value={`$${overview.total_cost_usd.toFixed(2)}`} icon="💰" accent="#f59e0b" />
        <MetricCard label="Avg Latency" value={`${overview.avg_latency_ms.toFixed(0)}ms`} icon="⚡" accent="#06b6d4" />
        <MetricCard label="Cost Saved" value={`$${overview.cost_saved_usd.toFixed(2)}`} icon="💎" accent="#10b981" />
      </div>

      {/* Charts Row */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 20, marginBottom: 24 }}>
        {/* Cost Trend */}
        <div className="glass-card">
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 20 }}>Cost Trend (30 Days)</h3>
          <ResponsiveContainer width="100%" height={280}>
            <AreaChart data={cost.daily_costs}>
              <defs>
                <linearGradient id="costGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a2a4a" />
              <XAxis dataKey="date" tick={{ fill: '#6a6a88', fontSize: 11 }} tickFormatter={d => d?.slice(5)} />
              <YAxis tick={{ fill: '#6a6a88', fontSize: 11 }} tickFormatter={v => `$${v}`} />
              <Tooltip content={<CustomTooltip />} />
              <Area type="monotone" dataKey="cost" stroke="#6366f1" fill="url(#costGradient)" strokeWidth={2} name="Cost" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Model Distribution */}
        <div className="glass-card">
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 20 }}>Model Distribution</h3>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={Object.entries(usage.requests_by_model).map(([name, value]) => ({ name, value }))}
                cx="50%" cy="50%" innerRadius={60} outerRadius={100}
                paddingAngle={3} dataKey="value"
              >
                {Object.keys(usage.requests_by_model).map((model, i) => (
                  <Cell key={model} fill={MODEL_COLORS[model] || COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
              <Legend
                wrapperStyle={{ fontSize: '0.75rem', color: '#9898b0' }}
                formatter={(value) => <span style={{ color: '#9898b0' }}>{value}</span>}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Status Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16 }}>
        <StatusCard label="Error Rate" value={`${(overview.error_rate * 100).toFixed(1)}%`} status={overview.error_rate < 0.05 ? 'good' : 'warning'} />
        <StatusCard label="Cache Hit Rate" value={`${(overview.cache_hit_rate * 100).toFixed(1)}%`} status={overview.cache_hit_rate > 0.1 ? 'good' : 'neutral'} />
        <StatusCard label="Total Tokens" value={`${(overview.total_tokens / 1_000_000).toFixed(1)}M`} status="neutral" />
      </div>
    </div>
  );
}


// ═══════════════════════════════════════════════════════════
// ── COST PAGE
// ═══════════════════════════════════════════════════════════

function CostPage({ cost }: { cost: CostData }) {
  return (
    <div className="animate-fade-in">
      <div style={{ marginBottom: 32 }}>
        <h2 style={{ fontSize: '1.8rem', fontWeight: 700 }}>Cost Analytics</h2>
        <p style={{ color: '#9898b0', marginTop: 4 }}>Understand where your LLM budget goes</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16, marginBottom: 32 }}>
        <MetricCard label="Total Cost" value={`$${cost.total_cost_usd.toFixed(2)}`} icon="💰" accent="#f59e0b" />
        <MetricCard label="Avg/Request" value={`$${cost.avg_cost_per_request.toFixed(4)}`} icon="📊" accent="#6366f1" />
        <MetricCard label="Requests" value={cost.total_requests.toLocaleString()} icon="📡" accent="#06b6d4" />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
        {/* Daily cost chart */}
        <div className="glass-card">
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 20 }}>Daily Cost</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={cost.daily_costs}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a2a4a" />
              <XAxis dataKey="date" tick={{ fill: '#6a6a88', fontSize: 11 }} tickFormatter={d => d?.slice(5)} />
              <YAxis tick={{ fill: '#6a6a88', fontSize: 11 }} tickFormatter={v => `$${v}`} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="cost" fill="#6366f1" radius={[6, 6, 0, 0]} name="Cost" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Cost by model */}
        <div className="glass-card">
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 20 }}>Cost by Model</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {Object.entries(cost.cost_by_model)
              .sort(([, a], [, b]) => b - a)
              .map(([model, modelCost]) => {
                const pct = (modelCost / cost.total_cost_usd) * 100;
                return (
                  <div key={model}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                      <span style={{ fontSize: '0.85rem', color: '#e8e8f0' }}>{model}</span>
                      <span style={{ fontSize: '0.85rem', fontWeight: 600, color: MODEL_COLORS[model] || '#9898b0' }}>${modelCost.toFixed(2)}</span>
                    </div>
                    <div style={{ height: 6, background: '#1a1a2e', borderRadius: 3, overflow: 'hidden' }}>
                      <div style={{
                        width: `${pct}%`,
                        height: '100%',
                        background: MODEL_COLORS[model] || '#6366f1',
                        borderRadius: 3,
                        transition: 'width 0.8s ease',
                      }} />
                    </div>
                  </div>
                );
              })}
          </div>
        </div>
      </div>
    </div>
  );
}


// ═══════════════════════════════════════════════════════════
// ── PERFORMANCE PAGE
// ═══════════════════════════════════════════════════════════

function PerformancePage({ latency }: { latency: LatencyData }) {
  return (
    <div className="animate-fade-in">
      <div style={{ marginBottom: 32 }}>
        <h2 style={{ fontSize: '1.8rem', fontWeight: 700 }}>Performance</h2>
        <p style={{ color: '#9898b0', marginTop: 4 }}>Latency percentiles and response times</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 32 }}>
        <MetricCard label="Avg Latency" value={`${latency.avg_latency_ms.toFixed(0)}ms`} icon="⚡" accent="#06b6d4" />
        <MetricCard label="P50" value={`${latency.p50_latency_ms.toFixed(0)}ms`} icon="📊" accent="#10b981" />
        <MetricCard label="P95" value={`${latency.p95_latency_ms.toFixed(0)}ms`} icon="📈" accent="#f59e0b" />
        <MetricCard label="P99" value={`${latency.p99_latency_ms.toFixed(0)}ms`} icon="🔥" accent="#ef4444" />
      </div>

      <div className="glass-card">
        <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 20 }}>Daily Latency Trend</h3>
        <ResponsiveContainer width="100%" height={350}>
          <AreaChart data={latency.daily_latency}>
            <defs>
              <linearGradient id="latencyGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#2a2a4a" />
            <XAxis dataKey="date" tick={{ fill: '#6a6a88', fontSize: 11 }} tickFormatter={d => d?.slice(5)} />
            <YAxis tick={{ fill: '#6a6a88', fontSize: 11 }} tickFormatter={v => `${v}ms`} />
            <Tooltip content={<CustomTooltip />} />
            <Area type="monotone" dataKey="avg_latency_ms" stroke="#06b6d4" fill="url(#latencyGrad)" strokeWidth={2} name="Avg Latency" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}


// ═══════════════════════════════════════════════════════════
// ── TRACES PAGE
// ═══════════════════════════════════════════════════════════

function TracesPage({ traces }: { traces: TraceListData }) {
  return (
    <div className="animate-fade-in">
      <div style={{ marginBottom: 32, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '1.8rem', fontWeight: 700 }}>Trace Explorer</h2>
          <p style={{ color: '#9898b0', marginTop: 4 }}>{traces.total.toLocaleString()} traces captured</p>
        </div>
      </div>

      <div className="glass-card" style={{ padding: 0, overflow: 'hidden' }}>
        <table className="data-table">
          <thead>
            <tr>
              <th>Time</th>
              <th>Model</th>
              <th>Prompt</th>
              <th>Tokens</th>
              <th>Cost</th>
              <th>Latency</th>
              <th>Status</th>
              <th>Cache</th>
            </tr>
          </thead>
          <tbody>
            {traces.traces.map((trace) => (
              <tr key={trace.id} style={{ cursor: 'pointer' }}>
                <td style={{ whiteSpace: 'nowrap', fontSize: '0.8rem' }}>
                  {new Date(trace.created_at).toLocaleTimeString()}
                </td>
                <td>
                  <span style={{
                    color: MODEL_COLORS[trace.model] || '#9898b0',
                    fontWeight: 600,
                    fontSize: '0.8rem',
                  }}>
                    {trace.model}
                  </span>
                </td>
                <td style={{ maxWidth: 250, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {trace.prompt}
                </td>
                <td style={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>
                  {trace.total_tokens || (trace.prompt_tokens + trace.completion_tokens)}
                </td>
                <td style={{ fontFamily: 'monospace', fontWeight: 600, color: '#f59e0b', fontSize: '0.8rem' }}>
                  ${trace.cost_usd?.toFixed(4)}
                </td>
                <td style={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>
                  {trace.latency_ms?.toFixed(0)}ms
                </td>
                <td>
                  <span className={`badge ${trace.status === 'success' ? 'badge-success' : 'badge-error'}`}>
                    {trace.status}
                  </span>
                </td>
                <td>
                  {trace.cache_hit && <span className="badge badge-success">HIT</span>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}


// ═══════════════════════════════════════════════════════════
// ── ERRORS PAGE
// ═══════════════════════════════════════════════════════════

function ErrorsPage({ errors }: { errors: ErrorData }) {
  return (
    <div className="animate-fade-in">
      <div style={{ marginBottom: 32 }}>
        <h2 style={{ fontSize: '1.8rem', fontWeight: 700 }}>Error Monitoring</h2>
        <p style={{ color: '#9898b0', marginTop: 4 }}>Track and analyze LLM failures</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 16, marginBottom: 32 }}>
        <MetricCard label="Total Errors" value={errors.total_errors.toLocaleString()} icon="🚨" accent="#ef4444" />
        <MetricCard label="Error Rate" value={`${(errors.error_rate * 100).toFixed(1)}%`} icon="📉" accent="#f59e0b" />
      </div>

      {/* Error types */}
      <div className="glass-card" style={{ marginBottom: 24 }}>
        <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 16 }}>Error Types</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {Object.entries(errors.errors_by_type).map(([type, count]) => (
            <div key={type} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '0.875rem', color: '#e8e8f0' }}>{type}</span>
              <span className="badge badge-error">{count}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Recent errors */}
      <div className="glass-card" style={{ padding: 0, overflow: 'hidden' }}>
        <div style={{ padding: '16px 24px', borderBottom: '1px solid #2a2a4a' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600 }}>Recent Errors</h3>
        </div>
        <table className="data-table">
          <thead>
            <tr>
              <th>Time</th>
              <th>Model</th>
              <th>Error</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {errors.recent_errors.map((err) => (
              <tr key={err.id}>
                <td style={{ fontSize: '0.8rem', whiteSpace: 'nowrap' }}>
                  {new Date(err.created_at).toLocaleString()}
                </td>
                <td style={{ color: MODEL_COLORS[err.model] || '#9898b0', fontWeight: 600, fontSize: '0.85rem' }}>
                  {err.model}
                </td>
                <td style={{ color: '#ef4444' }}>{err.error_message}</td>
                <td><span className="badge badge-error">{err.status_code}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}


// ═══════════════════════════════════════════════════════════
// ── CACHE & SAVINGS PAGE
// ═══════════════════════════════════════════════════════════

function CachePage({ overview }: { overview: OverviewData }) {
  const cacheHits = Math.round(overview.total_requests * overview.cache_hit_rate);
  const savedPerHit = overview.total_cost_usd / overview.total_requests;
  const estimatedSaving = cacheHits * savedPerHit;

  // ROI projection
  const monthlyRequests = overview.total_requests;
  const monthlyCost = overview.total_cost_usd;
  const projectedCacheSavings = monthlyCost * 0.30;
  const projectedModelSavings = monthlyCost * 0.12;
  const totalProjected = projectedCacheSavings + projectedModelSavings;

  return (
    <div className="animate-fade-in">
      <div style={{ marginBottom: 32 }}>
        <h2 style={{ fontSize: '1.8rem', fontWeight: 700 }}>Cache & Savings</h2>
        <p style={{ color: '#9898b0', marginTop: 4 }}>Reducing costs through intelligent caching</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 32 }}>
        <MetricCard label="Cache Hit Rate" value={`${(overview.cache_hit_rate * 100).toFixed(1)}%`} icon="🎯" accent="#10b981" />
        <MetricCard label="Cache Hits" value={cacheHits.toLocaleString()} icon="💎" accent="#6366f1" />
        <MetricCard label="Est. Saved" value={`$${estimatedSaving.toFixed(2)}`} icon="💰" accent="#f59e0b" />
        <MetricCard label="Tokens Saved" value={`${(cacheHits * 500).toLocaleString()}`} icon="📊" accent="#8b5cf6" />
      </div>

      {/* ROI Calculator */}
      <div className="glass-card" style={{
        background: 'linear-gradient(135deg, rgba(99,102,241,0.08), rgba(139,92,246,0.08))',
        borderColor: 'rgba(99,102,241,0.2)',
      }}>
        <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: 20, display: 'flex', alignItems: 'center', gap: 8 }}>
          <span>🚀</span> ROI Projection
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 24 }}>
          <div>
            <h4 style={{ color: '#9898b0', fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 12 }}>Current Spend</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              <Row label="Monthly Requests" value={monthlyRequests.toLocaleString()} />
              <Row label="Monthly Cost" value={`$${monthlyCost.toFixed(2)}`} valueColor="#ef4444" />
              <Row label="Avg Cost/Request" value={`$${(monthlyCost / monthlyRequests).toFixed(4)}`} />
            </div>
          </div>
          <div>
            <h4 style={{ color: '#9898b0', fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 12 }}>With PromptOps</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              <Row label="Cache Savings (30%)" value={`-$${projectedCacheSavings.toFixed(2)}`} valueColor="#10b981" />
              <Row label="Model Routing (12%)" value={`-$${projectedModelSavings.toFixed(2)}`} valueColor="#10b981" />
              <Row label="Total Saved" value={`$${totalProjected.toFixed(2)}/mo`} valueColor="#10b981" bold />
            </div>
          </div>
        </div>
        <div style={{
          marginTop: 20,
          padding: '12px 16px',
          background: 'rgba(16,185,129,0.1)',
          borderRadius: 10,
          border: '1px solid rgba(16,185,129,0.2)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}>
          <span style={{ fontSize: '0.9rem', color: '#10b981' }}>💰 Projected Annual Savings</span>
          <span style={{ fontSize: '1.3rem', fontWeight: 800, color: '#10b981' }}>${(totalProjected * 12).toFixed(0)}/year</span>
        </div>
      </div>
    </div>
  );
}


// ═══════════════════════════════════════════════════════════
// ── SHARED COMPONENTS
// ═══════════════════════════════════════════════════════════

function MetricCard({ label, value, icon, accent }: {
  label: string; value: string; icon: string; accent: string;
}) {
  return (
    <div className="metric-card" style={{ '--gradient-primary': `linear-gradient(135deg, ${accent}, ${accent}dd)` } as React.CSSProperties}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <div className="metric-value" style={{
            background: `linear-gradient(135deg, ${accent}, ${accent}cc)`,
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}>
            {value}
          </div>
          <div className="metric-label">{label}</div>
        </div>
        <span style={{ fontSize: '1.5rem', opacity: 0.7 }}>{icon}</span>
      </div>
    </div>
  );
}

function StatusCard({ label, value, status }: {
  label: string; value: string; status: 'good' | 'warning' | 'neutral';
}) {
  const colors = {
    good: { bg: 'rgba(16,185,129,0.08)', border: 'rgba(16,185,129,0.2)', dot: '#10b981' },
    warning: { bg: 'rgba(245,158,11,0.08)', border: 'rgba(245,158,11,0.2)', dot: '#f59e0b' },
    neutral: { bg: 'rgba(99,102,241,0.06)', border: 'rgba(99,102,241,0.15)', dot: '#6366f1' },
  };
  const c = colors[status];

  return (
    <div className="glass-card" style={{ background: c.bg, borderColor: c.border }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
        <div style={{ width: 8, height: 8, borderRadius: '50%', background: c.dot }} />
        <span style={{ fontSize: '0.8rem', color: '#9898b0', textTransform: 'uppercase', letterSpacing: '0.04em' }}>{label}</span>
      </div>
      <div style={{ fontSize: '1.5rem', fontWeight: 700, color: c.dot }}>{value}</div>
    </div>
  );
}

function Row({ label, value, valueColor = '#e8e8f0', bold = false }: {
  label: string; value: string; valueColor?: string; bold?: boolean;
}) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
      <span style={{ fontSize: '0.85rem', color: '#9898b0' }}>{label}</span>
      <span style={{ fontSize: '0.85rem', fontWeight: bold ? 700 : 600, color: valueColor }}>{value}</span>
    </div>
  );
}
