import Card from "components/ui/Card";

const verdictConfig = {
  dangerous: {
    emoji: "\u274C",
    bg: "bg-red-50 border-danger/30",
    title: "Do NOT click or respond!",
    color: "text-danger",
  },
  suspicious: {
    emoji: "\u26A0\uFE0F",
    bg: "bg-amber-50 border-warning/30",
    title: "Be very careful",
    color: "text-warning",
  },
  safe: {
    emoji: "\u2705",
    bg: "bg-emerald-50 border-safe/30",
    title: "This looks safe",
    color: "text-safe",
  },
};

export default function GrandmaResult({ result }) {
  const config = verdictConfig[result.threat_level] || verdictConfig.suspicious;

  return (
    <Card className={`${config.bg} border-2`}>
      <div className="text-center">
        <span className="text-6xl block mb-3">{config.emoji}</span>
        <h2 className={`text-2xl font-bold ${config.color} mb-2`}>
          {config.title}
        </h2>
        <p className="text-lg text-text-primary mb-4">
          {result.verdict_summary || "Analysis complete."}
        </p>
      </div>

      {result.consequence_warning && (
        <div className="rounded-xl bg-white/70 p-4 mb-3">
          <h3 className="text-base font-semibold text-text-primary mb-1">
            What could happen
          </h3>
          <p className="text-text-muted">{result.consequence_warning}</p>
        </div>
      )}

      {result.safe_action_suggestion && (
        <div className="rounded-xl bg-white/70 p-4">
          <h3 className="text-base font-semibold text-text-primary mb-1">
            What you should do
          </h3>
          <p className="text-text-muted">{result.safe_action_suggestion}</p>
        </div>
      )}
    </Card>
  );
}
