/**
 * API client for the PromptOps backend.
 * Uses a demo API key and falls back to mock data when the backend is unreachable.
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const DEMO_API_KEY = 'sq-demo-key-for-testing-only-1234567890';

async function fetchAPI<T>(path: string, options?: RequestInit): Promise<T> {
    try {
        const res = await fetch(`${API_URL}${path}`, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': DEMO_API_KEY,
                ...options?.headers,
            },
        });
        if (!res.ok) throw new Error(`API error: ${res.status}`);
        return res.json();
    } catch {
        console.warn(`[PromptOps] API unreachable, using mock data for ${path}`);
        return getMockData(path) as T;
    }
}

// ── API Functions ────────────────────────────────────────

export async function getOverview(days = 30) {
    return fetchAPI<OverviewData>(`/v1/analytics/overview?days=${days}`);
}

export async function getCostAnalytics(days = 30) {
    return fetchAPI<CostData>(`/v1/analytics/cost?days=${days}`);
}

export async function getLatencyAnalytics(days = 30) {
    return fetchAPI<LatencyData>(`/v1/analytics/latency?days=${days}`);
}

export async function getUsageAnalytics(days = 30) {
    return fetchAPI<UsageData>(`/v1/analytics/usage?days=${days}`);
}

export async function getErrorAnalytics(days = 30) {
    return fetchAPI<ErrorData>(`/v1/analytics/errors?days=${days}`);
}

export async function getTraces(page = 1, pageSize = 50) {
    return fetchAPI<TraceListData>(`/v1/traces?page=${page}&page_size=${pageSize}`);
}

// ── Types ────────────────────────────────────────────────

export interface OverviewData {
    total_requests: number;
    total_cost_usd: number;
    avg_latency_ms: number;
    error_rate: number;
    cache_hit_rate: number;
    cost_saved_usd: number;
    total_tokens: number;
    active_models: string[];
}

export interface CostData {
    total_cost_usd: number;
    total_requests: number;
    avg_cost_per_request: number;
    cost_by_model: Record<string, number>;
    daily_costs: Array<{ date: string; cost: number; requests: number }>;
}

export interface LatencyData {
    avg_latency_ms: number;
    p50_latency_ms: number;
    p95_latency_ms: number;
    p99_latency_ms: number;
    daily_latency: Array<{ date: string; avg_latency_ms: number }>;
}

export interface UsageData {
    total_requests: number;
    total_tokens: number;
    requests_by_model: Record<string, number>;
    requests_by_status: Record<string, number>;
    daily_requests: Array<{ date: string; requests: number }>;
}

export interface ErrorData {
    total_errors: number;
    error_rate: number;
    errors_by_type: Record<string, number>;
    recent_errors: Array<{
        id: string;
        model: string;
        error_message: string;
        status_code: number;
        created_at: string;
    }>;
}

export interface TraceListData {
    traces: TraceData[];
    total: number;
    page: number;
    page_size: number;
}

export interface TraceData {
    id: string;
    project_id: string;
    trace_id: string;
    model: string;
    provider: string;
    prompt: string;
    completion: string;
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
    cost_usd: number;
    latency_ms: number;
    status: string;
    error_message: string | null;
    cache_hit: boolean;
    metadata: Record<string, unknown>;
    environment: string;
    created_at: string;
}

// ── Mock Data ────────────────────────────────────────────

function generateDailyData(days: number) {
    const data = [];
    const now = new Date();
    for (let i = days - 1; i >= 0; i--) {
        const d = new Date(now);
        d.setDate(d.getDate() - i);
        data.push({
            date: d.toISOString().split('T')[0],
            cost: +(Math.random() * 20 + 5).toFixed(2),
            requests: Math.floor(Math.random() * 500 + 100),
            avg_latency_ms: +(Math.random() * 400 + 200).toFixed(0),
        });
    }
    return data;
}

function getMockData(path: string): unknown {
    const daily = generateDailyData(30);

    if (path.includes('/overview')) {
        return {
            total_requests: 10247,
            total_cost_usd: 487.32,
            avg_latency_ms: 423.5,
            error_rate: 0.058,
            cache_hit_rate: 0.152,
            cost_saved_usd: 73.42,
            total_tokens: 8_450_000,
            active_models: ['gpt-4o', 'gpt-4o-mini', 'gpt-3.5-turbo', 'claude-3.5-sonnet', 'claude-3-haiku'],
        };
    }
    if (path.includes('/cost')) {
        return {
            total_cost_usd: 487.32,
            total_requests: 10247,
            avg_cost_per_request: 0.0476,
            cost_by_model: {
                'gpt-4o': 198.45,
                'gpt-4o-mini': 42.18,
                'gpt-3.5-turbo': 15.67,
                'claude-3.5-sonnet': 165.32,
                'claude-3-haiku': 65.70,
            },
            daily_costs: daily.map(d => ({ date: d.date, cost: d.cost, requests: d.requests })),
        };
    }
    if (path.includes('/latency')) {
        return {
            avg_latency_ms: 423.5,
            p50_latency_ms: 345,
            p95_latency_ms: 892,
            p99_latency_ms: 2340,
            daily_latency: daily.map(d => ({ date: d.date, avg_latency_ms: d.avg_latency_ms })),
        };
    }
    if (path.includes('/usage')) {
        return {
            total_requests: 10247,
            total_tokens: 8_450_000,
            requests_by_model: {
                'gpt-4o': 3589,
                'gpt-4o-mini': 3073,
                'gpt-3.5-turbo': 1537,
                'claude-3.5-sonnet': 1024,
                'claude-3-haiku': 1024,
            },
            requests_by_status: { success: 9652, error: 423, timeout: 172 },
            daily_requests: daily.map(d => ({ date: d.date, requests: d.requests })),
        };
    }
    if (path.includes('/errors')) {
        return {
            total_errors: 595,
            error_rate: 0.058,
            errors_by_type: { 'Rate limit exceeded': 245, 'Context length exceeded': 183, 'Timeout': 167 },
            recent_errors: [
                { id: '1', model: 'gpt-4o', error_message: 'Rate limit exceeded', status_code: 429, created_at: new Date().toISOString() },
                { id: '2', model: 'claude-3.5-sonnet', error_message: 'Context length exceeded', status_code: 400, created_at: new Date().toISOString() },
                { id: '3', model: 'gpt-4o-mini', error_message: 'Service temporarily unavailable', status_code: 503, created_at: new Date().toISOString() },
            ],
        };
    }
    if (path.includes('/traces')) {
        const models = ['gpt-4o', 'gpt-4o-mini', 'gpt-3.5-turbo', 'claude-3.5-sonnet', 'claude-3-haiku'];
        const statuses = ['success', 'success', 'success', 'success', 'error'];
        const prompts = [
            'Summarize this customer complaint',
            'Translate to Turkish',
            'Extract entities from contract',
            'Generate product description',
            'Classify support ticket',
        ];
        return {
            traces: Array.from({ length: 50 }, (_, i) => ({
                id: `trace-${i}`,
                project_id: 'demo',
                trace_id: `trace-${1000 + i}`,
                model: models[i % models.length],
                provider: i % 5 < 3 ? 'openai' : 'anthropic',
                prompt: prompts[i % prompts.length],
                completion: 'Generated response...',
                prompt_tokens: Math.floor(Math.random() * 1500 + 100),
                completion_tokens: Math.floor(Math.random() * 800 + 50),
                total_tokens: 0,
                cost_usd: +(Math.random() * 0.1).toFixed(4),
                latency_ms: +(Math.random() * 800 + 150).toFixed(0),
                status: statuses[i % statuses.length],
                error_message: statuses[i % statuses.length] === 'error' ? 'Rate limit exceeded' : null,
                cache_hit: Math.random() < 0.15,
                metadata: { category: 'support' },
                environment: 'production',
                created_at: new Date(Date.now() - i * 3600000).toISOString(),
            })),
            total: 10247,
            page: 1,
            page_size: 50,
        };
    }
    return {};
}
