"use client";

import { useEffect, useMemo, useState } from "react";
import type React from "react";

import {
  createApiKey,
  createDashboard,
  createDashboardTemplate,
  createSavedQuery,
  createScheduledReport,
  deleteScheduledReport,
  fetchApiKeys,
  fetchDashboards,
  fetchEvents,
  fetchReportHistory,
  fetchScheduledReports,
  fetchWidgetData,
  getLiveDashboardWebSocketUrl,
  getMe,
  getReportDownloadUrl,
  ingestBatchEvents,
  ingestSingleEvent,
  inviteUser,
  runScheduledReportNow,
  testWebhook,
  updateDashboard,
  updateWidget,
  uploadCsv,
  createWidget,
  type ApiKey,
  type Dashboard,
  type EventItem,
  type LiveSocketMessage,
  type LiveSocketStatus,
  type ReportFormat,
  type ReportFrequency,
  type ReportHistory,
  type ScheduledReport,
  type User,
  type Widget,
  type WidgetData,
} from "../lib/api";

import MessageBanner from "../components/common/MessageBanner";
import StatusCard from "../components/common/StatusCard";
import DashboardSection from "../components/dashboard/DashboardSection";
import EventsTable from "../components/events/EventsTable";
import ApiKeysSection from "../components/ingestion/ApiKeysSection";
import IngestionSection from "../components/ingestion/IngestionSection";
import InviteUserForm from "../components/invite/InviteUserForm";
import DashboardHeader from "../components/layout/DashboardHeader";
import RealtimeSection from "../components/realtime/RealtimeSection";
import ReportsSection from "../components/reports/ReportsSection";

type LiveAlert = {
  id: number;
  title?: string;
  message: string;
  created_at?: string | null;
  alert_rule?: string | null;
};

export default function HomePage() {
  const [user, setUser] = useState<User | null>(null);
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [role, setRole] = useState<"admin" | "analyst" | "viewer">("viewer");
  const [message, setMessage] = useState("");

  const [events, setEvents] = useState<EventItem[]>([]);
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const [dashboards, setDashboards] = useState<Dashboard[]>([]);
  const [activeDashboardId, setActiveDashboardId] = useState<number | null>(null);
  const [widgetData, setWidgetData] = useState<Record<number, WidgetData>>({});
  const [isFullscreen, setIsFullscreen] = useState(false);

  const [scheduledReports, setScheduledReports] = useState<ScheduledReport[]>([]);
  const [reportHistory, setReportHistory] = useState<ReportHistory[]>([]);
  const [reportName, setReportName] = useState("Daily Dashboard Summary");
  const [reportFrequency, setReportFrequency] = useState<ReportFrequency>("daily");
  const [reportFormat, setReportFormat] = useState<ReportFormat>("pdf");
  const [reportRecipients, setReportRecipients] = useState("");
  const [reportNextRunAt, setReportNextRunAt] = useState(() => {
    const date = new Date(Date.now() + 5 * 60 * 1000);
    return date.toISOString().slice(0, 16);
  });

  const [liveStatus, setLiveStatus] = useState<LiveSocketStatus>("disconnected");
  const [liveEvents, setLiveEvents] = useState<EventItem[]>([]);
  const [liveAlerts, setLiveAlerts] = useState<LiveAlert[]>([]);

  const activeDashboard = useMemo(
    () => dashboards.find((item) => item.id === activeDashboardId) || null,
    [dashboards, activeDashboardId]
  );

  async function loadReportsData() {
    const [scheduledData, historyData] = await Promise.all([
      fetchScheduledReports().catch(() => []),
      fetchReportHistory().catch(() => []),
    ]);

    setScheduledReports(scheduledData);
    setReportHistory(historyData);
  }

  async function loadData() {
    const [eventData, keyData, dashboardData] = await Promise.all([
      fetchEvents(),
      fetchApiKeys().catch(() => []),
      fetchDashboards().catch(() => []),
    ]);

    setEvents(eventData);
    setApiKeys(keyData);
    setDashboards(dashboardData);
    await loadReportsData();

    if (!activeDashboardId && dashboardData.length > 0) {
      setActiveDashboardId(dashboardData[0].id);
    }
  }

  async function loadWidgetData(dashboard?: Dashboard | null) {
    const selectedDashboard = dashboard || activeDashboard;
    if (!selectedDashboard) return;

    const result: Record<number, WidgetData> = {};

    await Promise.all(
      selectedDashboard.widgets.map(async (widget) => {
        try {
          result[widget.id] = await fetchWidgetData(widget.id);
        } catch {
          result[widget.id] = {
            widget_id: widget.id,
            type: widget.widget_type,
            data: [],
            value: 0,
          };
        }
      })
    );

    setWidgetData(result);
  }

  useEffect(() => {
    getMe()
      .then(async (data) => {
        setUser(data);
        await loadData();
      })
      .catch(() => {
        window.location.href = "/login";
      });
  }, []);

  useEffect(() => {
    if (activeDashboard) {
      loadWidgetData(activeDashboard);
    }
  }, [activeDashboardId, dashboards.length]);

  useEffect(() => {
    if (!activeDashboard) return;

    const interval = setInterval(async () => {
      await loadData();
      await loadWidgetData(activeDashboard);
    }, activeDashboard.auto_refresh_interval * 1000);

    return () => clearInterval(interval);
  }, [activeDashboard?.id, activeDashboard?.auto_refresh_interval]);

  useEffect(() => {
    if (!user) return;

    let socket: WebSocket | null = null;
    let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
    let shouldReconnect = true;

    const connectSocket = () => {
      setLiveStatus((current) =>
        current === "disconnected" ? "connecting" : "reconnecting"
      );

      socket = new WebSocket(getLiveDashboardWebSocketUrl());

      socket.onopen = () => {
        setLiveStatus("connected");
        socket?.send(JSON.stringify({ type: "ping" }));
      };

      socket.onmessage = async (event) => {
        try {
          const data = JSON.parse(event.data) as LiveSocketMessage;

          if (data.type === "event_created" || data.type === "event_processed") {
            setLiveEvents((current) => [data.event, ...current].slice(0, 20));
            setEvents((current) => {
              const withoutDuplicate = current.filter((item) => item.id !== data.event.id);
              return [data.event, ...withoutDuplicate].slice(0, 100);
            });
          }

          if (data.type === "dashboard_refresh") {
            await loadData();
            await loadWidgetData(activeDashboard);
          }

          if (data.type === "alert_triggered") {
            setLiveAlerts((current) => [data.notification, ...current].slice(0, 10));
          }
        } catch {
          // Ignore invalid websocket payloads
        }
      };

      socket.onerror = () => {
        setLiveStatus("error");
      };

      socket.onclose = () => {
        if (!shouldReconnect) {
          setLiveStatus("disconnected");
          return;
        }

        setLiveStatus("reconnecting");
        reconnectTimer = setTimeout(connectSocket, 3000);
      };
    };

    connectSocket();

    return () => {
      shouldReconnect = false;
      if (reconnectTimer) clearTimeout(reconnectTimer);
      if (socket) socket.close();
    };
  }, [user?.id, activeDashboard?.id]);

  async function handleInvite(e: React.FormEvent) {
    e.preventDefault();
    setMessage("");

    try {
      await inviteUser({ username, email, role });
      setMessage("User invited successfully");
      setUsername("");
      setEmail("");
      setRole("viewer");
    } catch {
      setMessage("Invite failed");
    }
  }

  async function runAction(action: () => Promise<unknown>, successMessage: string) {
    try {
      setMessage("Processing...");
      await action();
      await loadData();
      setMessage(successMessage);
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Action failed");
    }
  }

  async function setupDashboard() {
    try {
      setMessage("Creating dashboard...");

      const dashboard = await createDashboard({
        name: "Main Analytics Dashboard",
        description: "Org-wise analytics dashboard",
        access_type: "team",
        auto_refresh_interval: 30,
      });

      const query = await createSavedQuery({
        name: "All Events Query",
        event_name: "",
        metric: "count",
      });

      await createWidget(dashboard.id, {
        saved_query: query.id,
        title: "Total Events",
        widget_type: "kpi",
        time_range: "7d",
        position_x: 0,
        position_y: 0,
        width: 3,
        height: 2,
      });

      await createWidget(dashboard.id, {
        saved_query: query.id,
        title: "Events Over Time",
        widget_type: "line",
        time_range: "7d",
        position_x: 3,
        position_y: 0,
        width: 6,
        height: 4,
      });

      await createWidget(dashboard.id, {
        saved_query: query.id,
        title: "Events By Type",
        widget_type: "bar",
        time_range: "7d",
        position_x: 0,
        position_y: 4,
        width: 6,
        height: 4,
      });

      await createWidget(dashboard.id, {
        saved_query: query.id,
        title: "Event Distribution",
        widget_type: "pie",
        time_range: "7d",
        position_x: 6,
        position_y: 4,
        width: 6,
        height: 4,
      });

      await loadData();
      setActiveDashboardId(dashboard.id);
      setMessage("Dashboard created successfully");
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Dashboard setup failed");
    }
  }

  async function handleTimeRangeChange(widget: Widget, time_range: "24h" | "7d" | "30d") {
    await updateWidget(widget.id, { time_range });
    await loadData();
  }

  async function handleRefreshChange(interval: number) {
    if (!activeDashboard) return;

    await updateDashboard(activeDashboard.id, {
      auto_refresh_interval: interval,
    });

    await loadData();
  }

  async function handleSharingChange(accessType: "team" | "public") {
    if (!activeDashboard) return;

    await updateDashboard(activeDashboard.id, {
      access_type: accessType,
    });

    await loadData();
  }

  async function handleCreateReport(e: React.FormEvent) {
    e.preventDefault();

    if (!activeDashboardId) {
      setMessage("Please create/select a dashboard first");
      return;
    }

    try {
      setMessage("Creating scheduled report...");

      await createScheduledReport({
        dashboard: activeDashboardId,
        name: reportName,
        frequency: reportFrequency,
        report_format: reportFormat,
        recipients: reportRecipients,
        is_active: true,
        next_run_at: new Date(reportNextRunAt).toISOString(),
      });

      await loadReportsData();
      setMessage("Scheduled report created successfully");
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Scheduled report creation failed");
    }
  }

  async function handleRunReportNow(reportId: number) {
    try {
      setMessage("Report generation started...");
      await runScheduledReportNow(reportId);

      setTimeout(async () => {
        await loadReportsData();
      }, 1500);

      setMessage("Report generation started. Refresh history after a few seconds.");
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Report generation failed");
    }
  }

  async function handleDeleteReport(reportId: number) {
    try {
      setMessage("Deleting scheduled report...");
      await deleteScheduledReport(reportId);
      await loadReportsData();
      setMessage("Scheduled report deleted");
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Delete failed");
    }
  }

  function downloadReport(historyId: number) {
    const token = localStorage.getItem("access");
    const url = getReportDownloadUrl(historyId);

    fetch(url, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then(async (res) => {
        if (!res.ok) {
          throw new Error("Download failed");
        }

        const blob = await res.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const anchor = document.createElement("a");

        anchor.href = downloadUrl;
        anchor.download = `report-${historyId}`;
        document.body.appendChild(anchor);
        anchor.click();
        anchor.remove();
        window.URL.revokeObjectURL(downloadUrl);
      })
      .catch((err) => {
        setMessage(err instanceof Error ? err.message : "Download failed");
      });
  }

  if (!user) {
    return (
      <main className="min-h-screen bg-gray-100 p-10 text-gray-900">
        Loading...
      </main>
    );
  }

  const canInvite = user.role === "owner" || user.role === "admin";
  const canManageApiKeys = user.role === "owner" || user.role === "admin";
  const canEditDashboard =
    user.role === "owner" || user.role === "admin" || user.role === "analyst";

  return (
    <main
      className={`min-h-screen bg-gray-100 p-8 text-gray-900 ${
        isFullscreen ? "fixed inset-0 z-50 overflow-auto bg-white" : ""
      }`}
    >
      <div className="mx-auto max-w-7xl">
        <DashboardHeader user={user} />

        <MessageBanner message={message} />

        <RealtimeSection
          liveStatus={liveStatus}
          liveEvents={liveEvents}
          liveAlerts={liveAlerts}
        />

        <div className="mb-6 grid grid-cols-1 gap-4 md:grid-cols-4">
          <StatusCard title="Signup" value="Done" />
          <StatusCard title="JWT Login" value="Done" />
          <StatusCard title="Org Isolation" value="Done" />
          <StatusCard title="Role Guard" value={user.role} />
        </div>

        <DashboardSection
          dashboards={dashboards}
          activeDashboard={activeDashboard}
          activeDashboardId={activeDashboardId}
          widgetData={widgetData}
          canEditDashboard={canEditDashboard}
          isFullscreen={isFullscreen}
          setupDashboard={setupDashboard}
          runAction={runAction}
          createTemplateAction={() => createDashboardTemplate("web_analytics")}
          setActiveDashboardId={setActiveDashboardId}
          setIsFullscreen={setIsFullscreen}
          handleRefreshChange={handleRefreshChange}
          handleSharingChange={handleSharingChange}
          handleTimeRangeChange={handleTimeRangeChange}
          loadWidgetData={() => loadWidgetData()}
        />

        <ReportsSection
          dashboards={dashboards}
          activeDashboardId={activeDashboardId}
          scheduledReports={scheduledReports}
          reportHistory={reportHistory}
          reportName={reportName}
          reportFrequency={reportFrequency}
          reportFormat={reportFormat}
          reportRecipients={reportRecipients}
          reportNextRunAt={reportNextRunAt}
          canEditDashboard={canEditDashboard}
          setActiveDashboardId={setActiveDashboardId}
          setReportName={setReportName}
          setReportFrequency={setReportFrequency}
          setReportFormat={setReportFormat}
          setReportRecipients={setReportRecipients}
          setReportNextRunAt={setReportNextRunAt}
          loadReportsData={loadReportsData}
          handleCreateReport={handleCreateReport}
          handleRunReportNow={handleRunReportNow}
          handleDeleteReport={handleDeleteReport}
          downloadReport={downloadReport}
        />

        <IngestionSection
          apiKeys={apiKeys}
          selectedFile={selectedFile}
          canManageApiKeys={canManageApiKeys}
          setSelectedFile={setSelectedFile}
          setMessage={setMessage}
          runAction={runAction}
          ingestSingleEventAction={ingestSingleEvent}
          ingestBatchEventsAction={ingestBatchEvents}
          createApiKeyAction={() => createApiKey()}
          uploadCsvAction={(file) => uploadCsv(file)}
          testWebhookAction={(apiKey) => testWebhook(apiKey)}
          loadData={loadData}
        />

        <ApiKeysSection apiKeys={apiKeys} />

        <EventsTable events={events} />

        <InviteUserForm
          canInvite={canInvite}
          username={username}
          email={email}
          role={role}
          setUsername={setUsername}
          setEmail={setEmail}
          setRole={setRole}
          handleInvite={handleInvite}
        />
      </div>
    </main>
  );
}
