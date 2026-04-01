import Card from "components/ui/Card";

const verdictEmoji = {
  dangerous: "\u274C",
  suspicious: "\u26A0\uFE0F",
  safe: "\u2705",
};

function timeAgo(dateStr) {
  if (!dateStr) return "";
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "Just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return `${days}d ago`;
}

export default function HistoryCards({ items }) {
  if (!items.length) {
    return (
      <p className="text-center text-lg text-text-muted py-8">
        No scans yet. Try checking something suspicious!
      </p>
    );
  }

  return (
    <div className="grid gap-3">
      {items.map((item) => (
        <Card key={item.scan_id} className="flex items-center gap-4">
          <span className="text-3xl">
            {verdictEmoji[item.threat_level] || "\u2753"}
          </span>
          <div className="flex-1 min-w-0">
            <p className="font-semibold text-text-primary capitalize">
              {item.threat_level}
            </p>
            <p className="text-sm text-text-muted truncate">
              {item.scan_type} scan {item.scam_pattern ? `\u2022 ${item.scam_pattern}` : ""}
            </p>
          </div>
          <span className="text-sm text-text-muted whitespace-nowrap">
            {timeAgo(item.created_at)}
          </span>
        </Card>
      ))}
    </div>
  );
}
