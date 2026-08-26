function DashboardCard({ icon: Icon, label, value, description }) {
  return (
    <div className="dashboard-card">
      <div className="dashboard-card-icon">
        <Icon size={19} />
      </div>
      <div className="dashboard-card-content">
        <span>{label}</span>
        <strong>{value}</strong>
        {description && <small>{description}</small>}
      </div>
    </div>
  );
}
export default DashboardCard;