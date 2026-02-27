"use client";

import { useCallback, useEffect, useState } from "react";
import { useUXMode } from "lib/ux-mode-context";
import { scans } from "lib/api";
import Card from "components/ui/Card";
import Button from "components/ui/Button";
import Spinner from "components/ui/Spinner";
import HistoryCards from "components/history/HistoryCards";
import HistoryTable from "components/history/HistoryTable";

const PAGE_SIZE = 20;

export default function HistoryPage() {
  const { isGrandmaMode } = useUXMode();
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchHistory = useCallback(async (currentOffset) => {
    setLoading(true);
    setError("");
    try {
      const data = await scans.history(PAGE_SIZE, currentOffset);
      setItems(data.items);
      setTotal(data.total);
    } catch (err) {
      setError(err.detail || "Failed to load history.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchHistory(offset);
  }, [offset, fetchHistory]);

  const hasNext = offset + PAGE_SIZE < total;
  const hasPrev = offset > 0;

  return (
    <div className="grid gap-6">
      <div>
        <h1 className={`font-bold text-text-primary ${isGrandmaMode ? "text-3xl" : "text-2xl"}`}>
          {isGrandmaMode ? "Your Past Checks" : "Scan History"}
        </h1>
        <p className={`text-text-muted mt-1 ${isGrandmaMode ? "text-lg" : "text-sm"}`}>
          {isGrandmaMode
            ? "Here's everything you've checked before."
            : `${total} total scans recorded.`}
        </p>
      </div>

      {error && (
        <div className="rounded-xl border border-danger/30 bg-red-50 p-4">
          <p className="text-danger font-medium">{error}</p>
        </div>
      )}

      {loading ? (
        <div className="flex justify-center py-12">
          <Spinner size="lg" />
        </div>
      ) : (
        <Card>
          {isGrandmaMode ? (
            <HistoryCards items={items} />
          ) : (
            <HistoryTable items={items} />
          )}

          {(hasNext || hasPrev) && (
            <div className="mt-4 flex items-center justify-between">
              <Button
                variant="secondary"
                size="sm"
                disabled={!hasPrev}
                onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))}
              >
                Previous
              </Button>
              <span className="text-sm text-text-muted">
                {offset + 1}–{Math.min(offset + PAGE_SIZE, total)} of {total}
              </span>
              <Button
                variant="secondary"
                size="sm"
                disabled={!hasNext}
                onClick={() => setOffset(offset + PAGE_SIZE)}
              >
                Next
              </Button>
            </div>
          )}
        </Card>
      )}
    </div>
  );
}
