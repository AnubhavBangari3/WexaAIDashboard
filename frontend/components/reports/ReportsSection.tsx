
"use client";

import type {
  Dashboard,
  ReportFormat,
  ReportFrequency,
  ReportHistory,
  ScheduledReport,
} from "../../lib/api";

export default function ReportsSection({
  dashboards,
  activeDashboardId,
  scheduledReports,
  reportHistory,
  reportName,
  reportFrequency,
  reportFormat,
  reportRecipients,
  reportNextRunAt,
  canEditDashboard,
  setActiveDashboardId,
  setReportName,
  setReportFrequency,
  setReportFormat,
  setReportRecipients,
  setReportNextRunAt,
  loadReportsData,
  handleCreateReport,
  handleRunReportNow,
  handleDeleteReport,
  downloadReport,
}: {
  dashboards: Dashboard[];
  activeDashboardId: number | null;
  scheduledReports: ScheduledReport[];
  reportHistory: ReportHistory[];
  reportName: string;
  reportFrequency: ReportFrequency;
  reportFormat: ReportFormat;
  reportRecipients: string;
  reportNextRunAt: string;
  canEditDashboard: boolean;
  setActiveDashboardId: (value: number | null) => void;
  setReportName: (value: string) => void;
  setReportFrequency: (value: ReportFrequency) => void;
  setReportFormat: (value: ReportFormat) => void;
  setReportRecipients: (value: string) => void;
  setReportNextRunAt: (value: string) => void;
  loadReportsData: () => Promise<void>;
  handleCreateReport: (e: React.FormEvent) => Promise<void>;
  handleRunReportNow: (reportId: number) => Promise<void>;
  handleDeleteReport: (reportId: number) => Promise<void>;
  downloadReport: (historyId: number) => void;
}) {
  return (
    <section className="mb-6 rounded-xl bg-white p-6 shadow">
      <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-2xl font-bold">Scheduled Reports</h2>
          <p className="text-sm text-gray-600">
            Schedule recurring dashboard reports, generate PDF/PNG snapshots,
            email reports and download report history.
          </p>
        </div>

        <button
          onClick={() => loadReportsData()}
          className="rounded bg-gray-900 px-4 py-2 text-white"
        >
          Refresh Reports
        </button>
      </div>

      <form onSubmit={handleCreateReport} className="mb-6 grid grid-cols-1 gap-3 md:grid-cols-3">
        <input
          className="rounded border p-3"
          placeholder="Report name"
          value={reportName}
          onChange={(e) => setReportName(e.target.value)}
          required
        />

        <select
          className="rounded border p-3"
          value={activeDashboardId || ""}
          onChange={(e) => setActiveDashboardId(Number(e.target.value))}
          required
        >
          <option value="">Select Dashboard</option>
          {dashboards.map((dashboard) => (
            <option key={dashboard.id} value={dashboard.id}>
              {dashboard.name}
            </option>
          ))}
        </select>

        <select
          className="rounded border p-3"
          value={reportFrequency}
          onChange={(e) => setReportFrequency(e.target.value as ReportFrequency)}
        >
          <option value="daily">Daily</option>
          <option value="weekly">Weekly</option>
          <option value="monthly">Monthly</option>
        </select>

        <select
          className="rounded border p-3"
          value={reportFormat}
          onChange={(e) => setReportFormat(e.target.value as ReportFormat)}
        >
          <option value="pdf">PDF</option>
          <option value="png">PNG</option>
        </select>

        <input
          type="email"
          className="rounded border p-3"
          placeholder="Recipient email"
          value={reportRecipients}
          onChange={(e) => setReportRecipients(e.target.value)}
        />

        <input
          type="datetime-local"
          className="rounded border p-3"
          value={reportNextRunAt}
          onChange={(e) => setReportNextRunAt(e.target.value)}
          required
        />

        <button
          disabled={!canEditDashboard}
          className="rounded bg-blue-600 px-4 py-3 text-white disabled:bg-gray-400 md:col-span-3"
        >
          Schedule Report
        </button>
      </form>

      <div className="mb-6">
        <h3 className="mb-3 text-lg font-bold">Scheduled Report List</h3>

        {scheduledReports.length === 0 ? (
          <p className="rounded border border-dashed p-4 text-gray-600">
            No scheduled reports created yet.
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full border text-left text-sm">
              <thead className="bg-gray-100">
                <tr>
                  <th className="border p-3">Name</th>
                  <th className="border p-3">Dashboard</th>
                  <th className="border p-3">Frequency</th>
                  <th className="border p-3">Format</th>
                  <th className="border p-3">Next Run</th>
                  <th className="border p-3">Active</th>
                  <th className="border p-3">Actions</th>
                </tr>
              </thead>
              <tbody>
                {scheduledReports.map((report) => (
                  <tr key={report.id}>
                    <td className="border p-3 font-semibold">{report.name}</td>
                    <td className="border p-3">{report.dashboard_name}</td>
                    <td className="border p-3">{report.frequency}</td>
                    <td className="border p-3 uppercase">{report.report_format}</td>
                    <td className="border p-3">
                      {new Date(report.next_run_at).toLocaleString()}
                    </td>
                    <td className="border p-3">{report.is_active ? "Yes" : "No"}</td>
                    <td className="border p-3">
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleRunReportNow(report.id)}
                          className="rounded bg-green-600 px-3 py-1 text-white"
                        >
                          Run Now
                        </button>
                        <button
                          onClick={() => handleDeleteReport(report.id)}
                          className="rounded bg-red-600 px-3 py-1 text-white"
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div>
        <h3 className="mb-3 text-lg font-bold">Report History / Archive</h3>

        {reportHistory.length === 0 ? (
          <p className="rounded border border-dashed p-4 text-gray-600">
            No generated reports yet. Click Run Now after creating a scheduled report.
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full border text-left text-sm">
              <thead className="bg-gray-100">
                <tr>
                  <th className="border p-3">Report</th>
                  <th className="border p-3">Dashboard</th>
                  <th className="border p-3">Format</th>
                  <th className="border p-3">Status</th>
                  <th className="border p-3">Generated At</th>
                  <th className="border p-3">Download</th>
                </tr>
              </thead>
              <tbody>
                {reportHistory.map((history) => (
                  <tr key={history.id}>
                    <td className="border p-3 font-semibold">{history.report_name}</td>
                    <td className="border p-3">{history.dashboard_name}</td>
                    <td className="border p-3 uppercase">{history.report_format}</td>
                    <td className="border p-3">
                      <span
                        className={`rounded px-2 py-1 text-xs font-bold ${
                          history.status === "success"
                            ? "bg-green-100 text-green-700"
                            : history.status === "failed"
                            ? "bg-red-100 text-red-700"
                            : "bg-yellow-100 text-yellow-700"
                        }`}
                      >
                        {history.status}
                      </span>
                      {history.error_message && (
                        <p className="mt-1 max-w-sm text-xs text-red-600">
                          {history.error_message}
                        </p>
                      )}
                    </td>
                    <td className="border p-3">
                      {new Date(history.generated_at).toLocaleString()}
                    </td>
                    <td className="border p-3">
                      {history.status === "success" ? (
                        <button
                          onClick={() => downloadReport(history.id)}
                          className="rounded bg-indigo-600 px-3 py-1 text-white"
                        >
                          Download
                        </button>
                      ) : (
                        "-"
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  );
}
