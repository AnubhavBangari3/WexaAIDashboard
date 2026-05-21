"use client";

import { useEffect, useState } from "react";
import {
  AlertRule,
  AlertHistory,
  NotificationItem,
  createAlertRule,
  deleteAlertRule,
  evaluateAlertRule,
  evaluateAllAlertRules,
  fetchAlertHistory,
  fetchAlertRules,
  fetchNotifications,
  muteAlertRule,
  unmuteAlertRule,
} from "@/lib/api";

export default function AlertsPage() {
  const [rules, setRules] = useState<AlertRule[]>([]);
  const [history, setHistory] = useState<AlertHistory[]>([]);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const [form, setForm] = useState({
    name: "High Event Volume",
    event_name: "page_view",
    operator: "gt" as "gt" | "gte" | "lt" | "lte" | "eq",
    threshold: 5,
    time_window_minutes: 10,
    enable_in_app: true,
    enable_email: false,
    email_to: "",
    enable_webhook: false,
    webhook_url: "",
  });

  async function loadData() {
    setLoading(true);

    try {
      const [rulesData, historyData, notificationsData] = await Promise.all([
        fetchAlertRules(),
        fetchAlertHistory(),
        fetchNotifications(),
      ]);

      setRules(rulesData);
      setHistory(historyData);
      setNotifications(notificationsData);
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  async function handleCreateAlert(e: React.FormEvent) {
    e.preventDefault();
    setMessage("");

    try {
      await createAlertRule({
        name: form.name,
        event_name: form.event_name,
        metric: "count",
        operator: form.operator,
        threshold: form.threshold,
        time_window_minutes: form.time_window_minutes,
        enable_in_app: form.enable_in_app,
        enable_email: form.enable_email,
        email_to: form.email_to,
        enable_webhook: form.enable_webhook,
        webhook_url: form.webhook_url,
      });

      setMessage("Alert rule created successfully.");
      await loadData();
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Failed to create alert.");
    }
  }

  async function runAction(action: () => Promise<unknown>, success: string) {
    setMessage("Processing...");

    try {
      await action();
      setMessage(success);
      await loadData();
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Action failed");
    }
  }

  return (
    <main className="min-h-screen bg-gray-100 p-8 text-gray-900">
      <div className="mx-auto max-w-7xl space-y-6">
        <div className="flex flex-wrap items-center justify-between gap-4 rounded-xl bg-white p-6 shadow">
          <div>
            <h1 className="text-3xl font-bold">Alerts & Notifications</h1>
            <p className="mt-2 text-gray-600">
              Threshold alerts, in-app notifications, email, webhook, mute and alert history.
            </p>
          </div>

          <div className="flex gap-3">
            <button
              onClick={() => (window.location.href = "/")}
              className="rounded bg-gray-800 px-4 py-2 text-white"
            >
              Dashboard
            </button>

            <button
              onClick={() =>
                runAction(evaluateAllAlertRules, "All alerts evaluated successfully")
              }
              className="rounded bg-blue-600 px-4 py-2 text-white"
            >
              Evaluate All
            </button>
          </div>
        </div>

        {message && (
          <div className="rounded-xl bg-yellow-100 p-4 font-semibold text-yellow-900">
            {message}
          </div>
        )}

        <form onSubmit={handleCreateAlert} className="rounded-xl bg-white p-6 shadow">
          <h2 className="mb-4 text-2xl font-bold">Create Alert Rule</h2>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-5">
            <input
              className="rounded border p-3"
              placeholder="Alert name"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
            />

            <input
              className="rounded border p-3"
              placeholder="Event name"
              value={form.event_name}
              onChange={(e) => setForm({ ...form, event_name: e.target.value })}
            />

            <select
              className="rounded border p-3"
              value={form.operator}
              onChange={(e) =>
                setForm({
                  ...form,
                  operator: e.target.value as "gt" | "gte" | "lt" | "lte" | "eq",
                })
              }
            >
              <option value="gt">Greater than</option>
              <option value="gte">Greater than equal</option>
              <option value="lt">Less than</option>
              <option value="lte">Less than equal</option>
              <option value="eq">Equal</option>
            </select>

            <input
              className="rounded border p-3"
              type="number"
              placeholder="Threshold"
              value={form.threshold}
              onChange={(e) =>
                setForm({ ...form, threshold: Number(e.target.value) })
              }
            />

            <input
              className="rounded border p-3"
              type="number"
              placeholder="Window minutes"
              value={form.time_window_minutes}
              onChange={(e) =>
                setForm({
                  ...form,
                  time_window_minutes: Number(e.target.value),
                })
              }
            />
          </div>

          <div className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-3">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={form.enable_in_app}
                onChange={(e) =>
                  setForm({ ...form, enable_in_app: e.target.checked })
                }
              />
              In-app notification
            </label>

            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={form.enable_email}
                onChange={(e) =>
                  setForm({ ...form, enable_email: e.target.checked })
                }
              />
              Email notification
            </label>

            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={form.enable_webhook}
                onChange={(e) =>
                  setForm({ ...form, enable_webhook: e.target.checked })
                }
              />
              Webhook notification
            </label>
          </div>

          <div className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2">
            <input
              className="rounded border p-3"
              placeholder="Email to"
              value={form.email_to}
              onChange={(e) => setForm({ ...form, email_to: e.target.value })}
            />

            <input
              className="rounded border p-3"
              placeholder="Webhook URL"
              value={form.webhook_url}
              onChange={(e) => setForm({ ...form, webhook_url: e.target.value })}
            />
          </div>

          <button className="mt-4 rounded bg-green-600 px-5 py-3 font-semibold text-white">
            Create Alert
          </button>
        </form>

        <section className="rounded-xl bg-white p-6 shadow">
          <h2 className="mb-4 text-2xl font-bold">Alert Rules</h2>

          {loading ? (
            <p className="text-gray-600">Loading...</p>
          ) : rules.length === 0 ? (
            <p className="text-gray-600">No alert rules yet.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full border text-left text-sm">
                <thead className="bg-gray-100">
                  <tr>
                    <th className="border p-3">Name</th>
                    <th className="border p-3">Event</th>
                    <th className="border p-3">Condition</th>
                    <th className="border p-3">Status</th>
                    <th className="border p-3">Last Value</th>
                    <th className="border p-3">Actions</th>
                  </tr>
                </thead>

                <tbody>
                  {rules.map((rule) => (
                    <tr key={rule.id}>
                      <td className="border p-3 font-semibold">{rule.name}</td>
                      <td className="border p-3">{rule.event_name || "All events"}</td>
                      <td className="border p-3">
                        count {rule.operator} {rule.threshold} in{" "}
                        {rule.time_window_minutes}m
                      </td>
                      <td className="border p-3">
                        <span className="rounded bg-gray-100 px-2 py-1 text-xs font-bold uppercase">
                          {rule.status}
                        </span>
                      </td>
                      <td className="border p-3">{rule.last_triggered_value || "-"}</td>
                      <td className="border p-3">
                        <div className="flex flex-wrap gap-2">
                          <button
                            onClick={() =>
                              runAction(
                                () => evaluateAlertRule(rule.id),
                                "Alert evaluated successfully"
                              )
                            }
                            className="rounded bg-blue-600 px-3 py-1 text-white"
                          >
                            Test
                          </button>

                          {rule.status === "muted" ? (
                            <button
                              onClick={() =>
                                runAction(
                                  () => unmuteAlertRule(rule.id),
                                  "Alert unmuted successfully"
                                )
                              }
                              className="rounded bg-green-600 px-3 py-1 text-white"
                            >
                              Unmute
                            </button>
                          ) : (
                            <button
                              onClick={() =>
                                runAction(
                                  () => muteAlertRule(rule.id, 60),
                                  "Alert muted successfully"
                                )
                              }
                              className="rounded bg-yellow-600 px-3 py-1 text-white"
                            >
                              Mute
                            </button>
                          )}

                          <button
                            onClick={() =>
                              runAction(
                                () => deleteAlertRule(rule.id),
                                "Alert deleted successfully"
                              )
                            }
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
        </section>

        <section className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <div className="rounded-xl bg-white p-6 shadow">
            <h2 className="mb-4 text-xl font-bold">Alert History</h2>

            {history.length === 0 ? (
              <p className="text-gray-600">No alert history yet.</p>
            ) : (
              <div className="space-y-3">
                {history.slice(0, 8).map((item) => (
                  <div key={item.id} className="rounded border p-4">
                    <div className="flex justify-between gap-3">
                      <p className="font-semibold">{item.alert_name}</p>
                      <span className="text-sm text-gray-500">{item.action}</span>
                    </div>
                    <p className="mt-2 text-sm text-gray-700">{item.message}</p>
                    <p className="mt-2 text-xs text-gray-500">
                      {new Date(item.created_at).toLocaleString()}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="rounded-xl bg-white p-6 shadow">
            <h2 className="mb-4 text-xl font-bold">Notifications</h2>

            {notifications.length === 0 ? (
              <p className="text-gray-600">No notifications yet.</p>
            ) : (
              <div className="space-y-3">
                {notifications.slice(0, 8).map((item) => (
                  <div key={item.id} className="rounded border p-4">
                    <div className="flex justify-between gap-3">
                      <p className="font-semibold">{item.title}</p>
                      <span className="text-sm text-gray-500">{item.channel}</span>
                    </div>
                    <p className="mt-2 text-sm text-gray-700">{item.message}</p>
                    <p className="mt-2 text-xs text-gray-500">
                      {item.status} - {new Date(item.created_at).toLocaleString()}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </section>
      </div>
    </main>
  );
}