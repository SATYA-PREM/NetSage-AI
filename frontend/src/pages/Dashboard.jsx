import {
  AlertTriangle,
  Bot,
  ClipboardList,
  ShieldCheck,
} from "lucide-react";
import { useEffect, useState } from "react";
import DashboardCard from "../components/DashboardCard";
import { getDashboard } from "../services/api";

function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadDashboard();
  }, []);

  async function loadDashboard() {
    try {
      setLoading(true);
      const response = await getDashboard();
      setData(response);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <section className="page-content">
        <div className="loading-page">Loading dashboard...</div>
      </section>
    );
  }

  const dashboard = data || {};

  return (
    <section className="page-content">
      <div className="page-title">
        <div>
          <div className="eyebrow">OPERATIONS OVERVIEW</div>
          <h1>NetSage dashboard</h1>
          <p>Monitor diagnosis activity, review outcomes and AI-human agreement.</p>
        </div>
      </div>

      {error && (
        <div className="error-banner">
          <AlertTriangle size={16} />
          {error}
        </div>
      )}

      <div className="dashboard-metrics">
        <DashboardCard
          icon={ClipboardList}
          label="Total cases"
          value={dashboard.total_cases ?? 0}
          description="Loaded troubleshooting cases"
        />
        <DashboardCard
          icon={Bot}
          label="Reviews"
          value={dashboard.review_count ?? 0}
          description="Human review decisions"
        />
        <DashboardCard
          icon={ShieldCheck}
          label="AI agreement"
          value={
            dashboard.ai_human_agreement_rate != null
              ? `${dashboard.ai_human_agreement_rate}%`
              : "—"
          }
          description="AI / human agreement"
        />
        <DashboardCard
          icon={AlertTriangle}
          label="Corrections"
          value={dashboard.responsible_ai_corrections ?? 0}
          description="Human corrections"
        />
      </div>

      <div className="dashboard-grid">
        <section className="panel">
          <div className="panel-head">
            <div>
              <h2>Review outcomes</h2>
              <p>Human oversight decisions.</p>
            </div>
          </div>
          <BarChart
            data={[
              ["Accepted", dashboard.accepted || 0],
              ["Edited", dashboard.edited || 0],
              ["Rejected", dashboard.rejected || 0],
            ]}
          />
        </section>

        <section className="panel">
          <div className="panel-head">
            <div>
              <h2>Issue types</h2>
              <p>Distribution across cases.</p>
            </div>
          </div>
          <BarChart data={Object.entries(dashboard.issue_types || {})} />
        </section>
      </div>
    </section>
  );
}

function BarChart({ data }) {
  if (!data.length) {
    return <div className="muted-box">No dashboard data yet.</div>;
  }
  const max = Math.max(1, ...data.map(([, value]) => Number(value) || 0));
  return (
    <div className="bars">
      {data.map(([label, value]) => (
        <div className="bar-row" key={label}>
          <div className="bar-label">
            <span>{label}</span>
            <strong>{value}</strong>
          </div>
          <div className="bar-track">
            <i style={{ width: `${(Number(value) / max) * 100}%` }} />
          </div>
        </div>
      ))}
    </div>
  );
}
export default Dashboard;