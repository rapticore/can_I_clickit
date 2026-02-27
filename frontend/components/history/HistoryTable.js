import Badge from "components/ui/Badge";

function threatBadgeVariant(level) {
  if (level === "dangerous") return "danger";
  if (level === "suspicious") return "warning";
  return "safe";
}

function formatDate(dateStr) {
  if (!dateStr) return "";
  return new Date(dateStr).toLocaleString();
}

export default function HistoryTable({ items }) {
  if (!items.length) {
    return (
      <p className="text-center text-sm text-text-muted py-8">
        No scan history. Run your first analysis from the Dashboard.
      </p>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-card-edge text-left text-text-muted">
            <th className="pb-2 pr-4 font-medium">Date</th>
            <th className="pb-2 pr-4 font-medium">Type</th>
            <th className="pb-2 pr-4 font-medium">Verdict</th>
            <th className="pb-2 pr-4 font-medium">Confidence</th>
            <th className="pb-2 pr-4 font-medium">Score</th>
            <th className="pb-2 pr-4 font-medium">Pattern</th>
            <th className="pb-2 pr-4 font-medium">Tier</th>
            <th className="pb-2 font-medium">Latency</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.scan_id} className="border-b border-card-edge/50">
              <td className="py-2.5 pr-4 whitespace-nowrap">{formatDate(item.created_at)}</td>
              <td className="py-2.5 pr-4 capitalize">{item.scan_type}</td>
              <td className="py-2.5 pr-4">
                <Badge variant={threatBadgeVariant(item.threat_level)}>
                  {item.threat_level}
                </Badge>
              </td>
              <td className="py-2.5 pr-4 capitalize">{item.confidence}</td>
              <td className="py-2.5 pr-4">{item.confidence_score}%</td>
              <td className="py-2.5 pr-4">{item.scam_pattern || "\u2014"}</td>
              <td className="py-2.5 pr-4 font-mono text-xs">{item.analysis_tier}</td>
              <td className="py-2.5">{item.latency_ms}ms</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
