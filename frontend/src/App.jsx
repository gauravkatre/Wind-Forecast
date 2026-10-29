import { useEffect, useMemo, useState } from "react";
import {
  ResponsiveContainer, LineChart, Line, BarChart, Bar,
  XAxis, YAxis, Tooltip, Legend, CartesianGrid,
} from "recharts";
import { getJSON } from "./api";
import "./styles.css";

const num = (v) => (v == null ? "–" : Math.round(v).toLocaleString("en-GB"));
const stamp = (iso) => (iso ? iso.slice(5, 16).replace("T", " ") : "–");

function Card({ title, value, unit = "MW", hint }) {
  return (
    <div className="card">
      <div className="card-title">{title}</div>
      <div className="card-value">{value}<span className="unit"> {unit}</span></div>
      {hint && <div className="card-hint">{hint}</div>}
    </div>
  );
}

function SeriesTooltip({ active, payload }) {
  if (!active || !payload?.length) return null;
  const p = payload[0].payload;
  return (
    <div className="tip">
      <b>{stamp(p.start_time)} UTC</b>
      <div>Actual: {num(p.actual_mw)} MW</div>
      <div>Forecast: {num(p.forecast_mw)} MW</div>
      <div>Error: {num(p.error_mw)} MW</div>
      <div className="muted">Forecast published: {stamp(p.publish_time)}</div>
    </div>
  );
}

export default function App() {
  const [cfg, setCfg] = useState(null);
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");
  const [cutoff, setCutoff] = useState("");
  const [series, setSeries] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [horizon, setHorizon] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getJSON("/api/config")
      .then((c) => { setCfg(c); setStart(c.range_start); setEnd(c.range_end); setCutoff(c.cutoff_local); })
      .catch((e) => { setError(e.message); setLoading(false); });
  }, []);

  useEffect(() => {
    if (!start || !end || !cutoff) return;
    setLoading(true); setError("");
    Promise.all([
      getJSON("/api/forecast/latest", { start, end, cutoff }),
      getJSON("/api/metrics", { start, end, cutoff }),
      getJSON("/api/horizon-error", { start, end }),
    ])
      .then(([s, m, h]) => { setSeries(s); setMetrics(m); setHorizon(h); })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [start, end, cutoff]);

  const o = metrics?.overall;
  const dayData = useMemo(() => (metrics?.by_day || []).map((d) => ({ ...d, label: d.day.slice(5) })), [metrics]);
  const horizonData = useMemo(() => horizon.map((h) => ({ ...h, label: `${h.horizon_from_h}–${h.horizon_to_h}h` })), [horizon]);

  const insight = !o?.n ? null : o.bias_mw > 0
    ? `On average the forecast was ${num(o.bias_mw)} MW higher than actual wind. Buying only against the forecast would have left you about ${num(o.bias_mw)} MW short per hour, to be covered at imbalance prices.`
    : `On average the forecast was ${num(-o.bias_mw)} MW lower than actual wind, so buying against the forecast would have meant over-buying.`;

  return (
    <div className="page">
      <header>
        <h1>UK Wind Forecast Portal</h1>
        <p className="muted">Day-ahead decision support: which wind forecast was available at decision time, and how accurate was it?</p>
      </header>

      {cfg?.using_sample_data && <div className="banner">Showing synthetic sample data, not real Elexon data.</div>}
      {error && <div className="banner err">Could not load data: {error}</div>}

      <section className="controls">
        <label>From <input type="date" value={start} min={cfg?.range_start} max={end} onChange={(e) => setStart(e.target.value)} /></label>
        <label>To <input type="date" value={end} min={start} max={cfg?.range_end} onChange={(e) => setEnd(e.target.value)} /></label>
        <label>Decision cutoff (D-1, UK time) <input type="time" value={cutoff} onChange={(e) => e.target.value && setCutoff(e.target.value)} /></label>
        {loading && <span className="muted">Loading…</span>}
      </section>

      {o?.n > 0 && (
        <>
          <section className="cards">
            <Card title="Mean abs. error (MAE)" value={num(o.mae_mw)} hint={`${o.nmae_pct}% of mean wind`} />
            <Card title="RMSE" value={num(o.rmse_mw)} />
            <Card title="Bias (forecast − actual)" value={(o.bias_mw > 0 ? "+" : "") + num(o.bias_mw)} hint={o.bias_mw > 0 ? "forecast too high" : "forecast too low"} />
            <Card title="90% of hours within" value={num(o.abs_error_p90_mw)} hint="absolute error" />
            <Card title="95% of hours within" value={num(o.abs_error_p95_mw)} hint="absolute error" />
            <Card title="Worst miss" value={num(o.abs_error_max_mw)} />
          </section>
          {insight && <div className="insight">{insight}</div>}
        </>
      )}

      <section className="panel">
        <h2>Actual vs latest forecast available at decision time</h2>
        <p className="muted">For each hour, the forecast with the latest publish time before the D-1 cutoff.</p>
        <ResponsiveContainer width="100%" height={320}>
          <LineChart data={series} margin={{ left: 10, right: 10 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="start_time" tickFormatter={(v) => v.slice(5, 10)} minTickGap={40} />
            <YAxis tickFormatter={num} width={60} />
            <Tooltip content={<SeriesTooltip />} />
            <Legend />
            <Line type="monotone" dataKey="actual_mw" name="Actual (MW)" stroke="#1d4ed8" dot={false} isAnimationActive={false} />
            <Line type="monotone" dataKey="forecast_mw" name="Forecast (MW)" stroke="#ea580c" dot={false} connectNulls={false} isAnimationActive={false} />
          </LineChart>
        </ResponsiveContainer>
      </section>

      <div className="grid2">
        <section className="panel">
          <h2>Daily error</h2>
          <p className="muted">Error varies a lot day to day; one average hides the bad days.</p>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={dayData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="label" minTickGap={12} />
              <YAxis tickFormatter={num} width={55} />
              <Tooltip formatter={(v) => `${num(v)} MW`} />
              <Bar dataKey="mae_mw" name="MAE" fill="#ea580c" isAnimationActive={false} />
            </BarChart>
          </ResponsiveContainer>
        </section>

        <section className="panel">
          <h2>Error vs forecast horizon</h2>
          <p className="muted">All published forecasts: how far ahead was it made?</p>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={horizonData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="label" />
              <YAxis tickFormatter={num} width={55} />
              <Tooltip formatter={(v) => `${num(v)} MW`} />
              <Legend />
              <Bar dataKey="mae_mw" name="MAE" fill="#1d4ed8" isAnimationActive={false} />
              <Bar dataKey="abs_error_p90_mw" name="P90 abs error" fill="#94a3b8" isAnimationActive={false} />
            </BarChart>
          </ResponsiveContainer>
        </section>
      </div>

      <footer className="muted">
        Data: Elexon BMRS (FUELHH wind actuals, WINDFOR forecasts), national level, Jan 2026. Accuracy is computed on hours where both a forecast and an actual exist.
      </footer>
    </div>
  );
}
