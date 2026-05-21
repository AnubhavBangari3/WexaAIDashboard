import type { EventItem, LiveSocketStatus } from "../../lib/api";

type LiveAlert = {
  id: number;
  title?: string;
  message: string;
  created_at?: string | null;
  alert_rule?: string | null;
};

export default function RealtimeSection({
  liveStatus,
  liveEvents,
  liveAlerts,
}: {
  liveStatus: LiveSocketStatus;
  liveEvents: EventItem[];
  liveAlerts: LiveAlert[];
}) {
  return (
    <section className="mb-6 rounded-xl bg-white p-6 shadow">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-2xl font-bold">Real-Time Features</h2>
          <p className="text-sm text-gray-500">
            WebSocket live dashboard updates, alert push, and live event stream.
          </p>
        </div>

        <span
          className={`rounded-full px-3 py-1 text-sm font-semibold ${
            liveStatus === "connected"
              ? "bg-green-100 text-green-700"
              : liveStatus === "reconnecting"
              ? "bg-yellow-100 text-yellow-700"
              : "bg-red-100 text-red-700"
          }`}
        >
          {liveStatus}
        </span>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <div className="rounded-lg border p-4">
          <h3 className="mb-3 font-bold">Live Event Stream</h3>

          {liveEvents.length === 0 ? (
            <p className="text-sm text-gray-500">No live events received yet.</p>
          ) : (
            <div className="max-h-64 space-y-2 overflow-auto">
              {liveEvents.map((event) => (
                <div
                  key={`${event.id}-${event.status}`}
                  className="rounded bg-gray-50 p-3 text-sm"
                >
                  <div className="flex justify-between gap-3">
                    <b>{event.event_name}</b>
                    <span>{event.status}</span>
                  </div>
                  <p className="text-xs text-gray-500">{event.received_at}</p>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="rounded-lg border p-4">
          <h3 className="mb-3 font-bold">Real-Time Alerts</h3>

          {liveAlerts.length === 0 ? (
            <p className="text-sm text-gray-500">No live alerts received yet.</p>
          ) : (
            <div className="max-h-64 space-y-2 overflow-auto">
              {liveAlerts.map((alert) => (
                <div
                  key={alert.id}
                  className="rounded bg-red-50 p-3 text-sm text-red-900"
                >
                  <b>{alert.title || alert.alert_rule || "Alert Triggered"}</b>
                  <p>{alert.message}</p>
                  <p className="text-xs">{alert.created_at}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
