
"use client";

import type { Dashboard, Widget, WidgetData } from "../../lib/api";
import WidgetCard from "./WidgetCard";

export default function DashboardSection({
  dashboards,
  activeDashboard,
  activeDashboardId,
  widgetData,
  canEditDashboard,
  isFullscreen,
  setupDashboard,
  runAction,
  createTemplateAction,
  setActiveDashboardId,
  setIsFullscreen,
  handleRefreshChange,
  handleSharingChange,
  handleTimeRangeChange,
  loadWidgetData,
}: {
  dashboards: Dashboard[];
  activeDashboard: Dashboard | null;
  activeDashboardId: number | null;
  widgetData: Record<number, WidgetData>;
  canEditDashboard: boolean;
  isFullscreen: boolean;
  setupDashboard: () => Promise<void>;
  runAction: (action: () => Promise<unknown>, successMessage: string) => Promise<void>;
  createTemplateAction: () => Promise<unknown>;
  setActiveDashboardId: (value: number | null) => void;
  setIsFullscreen: React.Dispatch<React.SetStateAction<boolean>>;
  handleRefreshChange: (interval: number) => Promise<void>;
  handleSharingChange: (accessType: "team" | "public") => Promise<void>;
  handleTimeRangeChange: (
    widget: Widget,
    timeRange: "24h" | "7d" | "30d"
  ) => Promise<void>;
  loadWidgetData: () => Promise<void>;
}) {
  return (
    <section className="mb-6 rounded-xl bg-white p-6 shadow">
      <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-2xl font-bold">Dashboards & Visualizations</h2>
          <p className="text-sm text-gray-600">
            Dashboard model, widgets, charts, saved queries, filters, sharing,
            auto-refresh and fullscreen mode.
          </p>
        </div>

        <div className="flex flex-wrap gap-2">
          <button
            onClick={setupDashboard}
            disabled={!canEditDashboard}
            className="rounded bg-blue-600 px-4 py-2 text-white disabled:bg-gray-400"
          >
            Create Dashboard
          </button>

          <button
            onClick={() => runAction(createTemplateAction, "Template dashboard created")}
            disabled={!canEditDashboard}
            className="rounded bg-purple-600 px-4 py-2 text-white disabled:bg-gray-400"
          >
            Web Analytics Template
          </button>

          <button
            onClick={() => setIsFullscreen((prev) => !prev)}
            className="rounded bg-gray-900 px-4 py-2 text-white"
          >
            {isFullscreen ? "Exit Fullscreen" : "Fullscreen"}
          </button>
        </div>
      </div>

      {dashboards.length === 0 ? (
        <div className="rounded-lg border border-dashed p-8 text-center">
          <h3 className="text-xl font-bold">No dashboard found</h3>
          <p className="mt-2 text-gray-600">
            Click Create Dashboard to generate KPI, Line, Bar and Pie widgets.
          </p>
        </div>
      ) : (
        <>
          <div className="mb-5 grid grid-cols-1 gap-3 md:grid-cols-4">
            <select
              value={activeDashboardId || ""}
              onChange={(e) => setActiveDashboardId(Number(e.target.value))}
              className="rounded border p-3"
            >
              {dashboards.map((dashboard) => (
                <option key={dashboard.id} value={dashboard.id}>
                  {dashboard.name}
                </option>
              ))}
            </select>

            <select
              value={activeDashboard?.auto_refresh_interval || 30}
              onChange={(e) => handleRefreshChange(Number(e.target.value))}
              className="rounded border p-3"
            >
              <option value={30}>Auto-refresh: 30s</option>
              <option value={60}>Auto-refresh: 1m</option>
              <option value={300}>Auto-refresh: 5m</option>
            </select>

            <select
              value={activeDashboard?.access_type || "team"}
              onChange={(e) =>
                handleSharingChange(e.target.value as "team" | "public")
              }
              className="rounded border p-3"
            >
              <option value="team">Team Only</option>
              <option value="public">Public Read-only</option>
            </select>

            <button
              onClick={() => loadWidgetData()}
              className="rounded bg-green-600 px-4 py-2 text-white"
            >
              Refresh Charts
            </button>
          </div>

          <div className="mb-4 rounded-lg bg-gray-50 p-4">
            <h3 className="text-lg font-bold">{activeDashboard?.name}</h3>
            <p className="text-sm text-gray-600">
              Sharing: <b>{activeDashboard?.access_type}</b> | Refresh:{" "}
              <b>{activeDashboard?.auto_refresh_interval}s</b>
            </p>
          </div>

          <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
            {activeDashboard?.widgets.map((widget) => (
              <WidgetCard
                key={widget.id}
                widget={widget}
                data={widgetData[widget.id]}
                onTimeRangeChange={handleTimeRangeChange}
              />
            ))}
          </div>
        </>
      )}
    </section>
  );
}
