const API_BASE_URL = "http://127.0.0.1:8000/api";

export type User = {
  id: number;
  username: string;
  email: string;
  role: "owner" | "admin" | "analyst" | "viewer";
  organization_id: number;
  organization_name: string;
};

export type EventItem = {
  id: number;
  event_name: string;
  source_type: string;
  payload: Record<string, unknown>;
  normalized_payload: Record<string, unknown>;
  status: "pending" | "processed" | "failed";
  error_message?: string | null;
  occurred_at: string;
  received_at: string;
};

export type ApiKey = {
  id: number;
  name: string;
  key: string;
  is_active: boolean;
  created_at: string;
  revoked_at: string | null;
};

export type Dashboard = {
  id: number;
  name: string;
  description: string;
  access_type: "team" | "public";
  auto_refresh_interval: number;
  is_template: boolean;
  template_type: string;
  widgets: Widget[];
  created_at: string;
  updated_at: string;
};

export type SavedQuery = {
  id: number;
  name: string;
  event_name: string;
  metric: string;
  group_by: string;
  created_at: string;
};

export type Widget = {
  id: number;
  dashboard: number;
  saved_query: number | null;
  saved_query_detail?: SavedQuery | null;
  title: string;
  widget_type: "line" | "bar" | "pie" | "kpi" | "table";
  time_range: "24h" | "7d" | "30d";
  position_x: number;
  position_y: number;
  width: number;
  height: number;
  config: Record<string, unknown>;
  created_at: string;
  updated_at: string;
};

export type WidgetData = {
  widget_id: number;
  type: string;
  title?: string;
  value?: number;
  data?: {
    name: string;
    value: number;
  }[];
};

export function getAccessToken() {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("access");
}

function authHeaders() {
  const token = getAccessToken();

  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };
}

async function parseResponse(res: Response) {
  const text = await res.text();

  if (!text) return null;

  try {
    return JSON.parse(text);
  } catch {
    throw new Error(text.slice(0, 500));
  }
}

export function saveTokens(access: string, refresh: string) {
  localStorage.setItem("access", access);
  localStorage.setItem("refresh", refresh);
}

export function logout() {
  localStorage.removeItem("access");
  localStorage.removeItem("refresh");
  window.location.href = "/login";
}

export async function signup(data: {
  username: string;
  email: string;
  password: string;
  organization_name: string;
}) {
  const res = await fetch(`${API_BASE_URL}/auth/signup/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  const dataRes = await parseResponse(res);
  if (!res.ok) throw new Error(JSON.stringify(dataRes));
  return dataRes;
}

export async function login(data: { email: string; password: string }) {
  const res = await fetch(`${API_BASE_URL}/auth/login/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  const dataRes = await parseResponse(res);
  if (!res.ok) throw new Error(JSON.stringify(dataRes));
  return dataRes;
}

export async function getMe(): Promise<User> {
  const res = await fetch(`${API_BASE_URL}/auth/me/`, {
    headers: authHeaders(),
  });

  const dataRes = await parseResponse(res);
  if (!res.ok) throw new Error("Unauthorized");
  return dataRes;
}

export async function inviteUser(data: {
  username: string;
  email: string;
  role: "admin" | "analyst" | "viewer";
}) {
  const res = await fetch(`${API_BASE_URL}/auth/invite/`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify(data),
  });

  const dataRes = await parseResponse(res);
  if (!res.ok) throw new Error(JSON.stringify(dataRes));
  return dataRes;
}

export async function fetchEvents(): Promise<EventItem[]> {
  const res = await fetch(`${API_BASE_URL}/ingestion/events/`, {
    headers: authHeaders(),
  });

  const dataRes = await parseResponse(res);
  if (!res.ok) throw new Error(JSON.stringify(dataRes));
  return dataRes;
}

export async function ingestSingleEvent() {
  const res = await fetch(`${API_BASE_URL}/ingestion/events/ingest/`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({
      event_name: "page_view",
      payload: {
        page: "/home",
        user_id: 101,
        device: "chrome",
      },
    }),
  });

  const dataRes = await parseResponse(res);
  if (!res.ok) throw new Error(JSON.stringify(dataRes));
  return dataRes;
}

export async function ingestBatchEvents() {
  const res = await fetch(`${API_BASE_URL}/ingestion/events/batch/`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({
      events: [
        {
          event_name: "button_click",
          payload: {
            button: "signup",
          },
        },
        {
          event_name: "purchase",
          payload: {
            amount: 999,
            currency: "INR",
          },
        },
      ],
    }),
  });

  const dataRes = await parseResponse(res);
  if (!res.ok) throw new Error(JSON.stringify(dataRes));
  return dataRes;
}

export async function createApiKey(name = "Frontend Test Key"): Promise<ApiKey> {
  const res = await fetch(`${API_BASE_URL}/ingestion/api-keys/`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ name }),
  });

  const dataRes = await parseResponse(res);
  if (!res.ok) throw new Error(JSON.stringify(dataRes));
  return dataRes;
}

export async function fetchApiKeys(): Promise<ApiKey[]> {
  const res = await fetch(`${API_BASE_URL}/ingestion/api-keys/`, {
    headers: authHeaders(),
  });

  const dataRes = await parseResponse(res);
  if (!res.ok) throw new Error(JSON.stringify(dataRes));
  return dataRes;
}

export async function testWebhook(apiKey: string) {
  const res = await fetch(`${API_BASE_URL}/ingestion/webhook/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": apiKey,
    },
    body: JSON.stringify({
      event_name: "external_payment_success",
      payload: {
        payment_id: "pay_123",
        amount: 1200,
      },
    }),
  });

  const dataRes = await parseResponse(res);
  if (!res.ok) throw new Error(JSON.stringify(dataRes));
  return dataRes;
}

export async function uploadCsv(file: File) {
  const token = getAccessToken();
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE_URL}/ingestion/events/csv-upload/`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: formData,
  });

  const dataRes = await parseResponse(res);
  if (!res.ok) throw new Error(JSON.stringify(dataRes));
  return dataRes;
}

export async function fetchDashboards(): Promise<Dashboard[]> {
  const res = await fetch(`${API_BASE_URL}/dashboards/`, {
    headers: authHeaders(),
  });

  const dataRes = await parseResponse(res);
  if (!res.ok) throw new Error(JSON.stringify(dataRes));
  return dataRes;
}

export async function createDashboard(data: {
  name: string;
  description?: string;
  access_type?: "team" | "public";
  auto_refresh_interval?: number;
}): Promise<Dashboard> {
  const res = await fetch(`${API_BASE_URL}/dashboards/`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify(data),
  });

  const dataRes = await parseResponse(res);
  if (!res.ok) throw new Error(JSON.stringify(dataRes));
  return dataRes;
}

export async function updateDashboard(
  dashboardId: number,
  data: Partial<Dashboard>
): Promise<Dashboard> {
  const res = await fetch(`${API_BASE_URL}/dashboards/${dashboardId}/`, {
    method: "PUT",
    headers: authHeaders(),
    body: JSON.stringify(data),
  });

  const dataRes = await parseResponse(res);
  if (!res.ok) throw new Error(JSON.stringify(dataRes));
  return dataRes;
}

export async function deleteDashboard(dashboardId: number) {
  const res = await fetch(`${API_BASE_URL}/dashboards/${dashboardId}/`, {
    method: "DELETE",
    headers: authHeaders(),
  });

  const dataRes = await parseResponse(res);
  if (!res.ok) throw new Error(JSON.stringify(dataRes));
  return dataRes;
}

export async function createDashboardTemplate(
  template_type: "web_analytics" | "sales"
): Promise<Dashboard> {
  const res = await fetch(`${API_BASE_URL}/dashboards/templates/create/`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ template_type }),
  });

  const dataRes = await parseResponse(res);
  if (!res.ok) throw new Error(JSON.stringify(dataRes));
  return dataRes;
}

export async function fetchSavedQueries(): Promise<SavedQuery[]> {
  const res = await fetch(`${API_BASE_URL}/dashboards/saved-queries/`, {
    headers: authHeaders(),
  });

  const dataRes = await parseResponse(res);
  if (!res.ok) throw new Error(JSON.stringify(dataRes));
  return dataRes;
}

export async function createSavedQuery(data: {
  name: string;
  event_name?: string;
  metric?: string;
  group_by?: string;
}): Promise<SavedQuery> {
  const res = await fetch(`${API_BASE_URL}/dashboards/saved-queries/`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify(data),
  });

  const dataRes = await parseResponse(res);
  if (!res.ok) throw new Error(JSON.stringify(dataRes));
  return dataRes;
}

export async function createWidget(
  dashboardId: number,
  data: {
    saved_query?: number | null;
    title: string;
    widget_type: "line" | "bar" | "pie" | "kpi" | "table";
    time_range?: "24h" | "7d" | "30d";
    position_x?: number;
    position_y?: number;
    width?: number;
    height?: number;
    config?: Record<string, unknown>;
  }
): Promise<Widget> {
  const res = await fetch(`${API_BASE_URL}/dashboards/${dashboardId}/widgets/`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify(data),
  });

  const dataRes = await parseResponse(res);
  if (!res.ok) throw new Error(JSON.stringify(dataRes));
  return dataRes;
}

export async function updateWidget(
  widgetId: number,
  data: Partial<Widget>
): Promise<Widget> {
  const res = await fetch(`${API_BASE_URL}/dashboards/widgets/${widgetId}/`, {
    method: "PUT",
    headers: authHeaders(),
    body: JSON.stringify(data),
  });

  const dataRes = await parseResponse(res);
  if (!res.ok) throw new Error(JSON.stringify(dataRes));
  return dataRes;
}

export async function deleteWidget(widgetId: number) {
  const res = await fetch(`${API_BASE_URL}/dashboards/widgets/${widgetId}/`, {
    method: "DELETE",
    headers: authHeaders(),
  });

  const dataRes = await parseResponse(res);
  if (!res.ok) throw new Error(JSON.stringify(dataRes));
  return dataRes;
}

export async function fetchWidgetData(widgetId: number): Promise<WidgetData> {
  const res = await fetch(`${API_BASE_URL}/dashboards/widgets/${widgetId}/data/`, {
    headers: authHeaders(),
  });

  const dataRes = await parseResponse(res);
  if (!res.ok) throw new Error(JSON.stringify(dataRes));
  return dataRes;
}


export type AlertStatus = "active" | "triggered" | "resolved" | "muted";
export type AlertOperator = "gt" | "gte" | "lt" | "lte" | "eq";

export type AlertRule = {
  id: number;
  name: string;
  event_name: string;
  metric: string;
  operator: AlertOperator;
  threshold: string;
  time_window_minutes: number;
  enable_in_app: boolean;
  enable_email: boolean;
  email_to: string;
  enable_webhook: boolean;
  webhook_url: string;
  status: AlertStatus;
  muted_until: string | null;
  last_triggered_value: string | null;
  last_evaluated_at: string | null;
  created_at: string;
  updated_at: string;
};

export type AlertHistory = {
  id: number;
  alert_rule: number;
  alert_name: string;
  action: string;
  triggered_value: string | null;
  threshold: string | null;
  message: string;
  created_at: string;
};

export type NotificationItem = {
  id: number;
  alert_rule: number;
  alert_name: string;
  channel: "in_app" | "email" | "webhook";
  title: string;
  message: string;
  status: "pending" | "sent" | "failed";
  error_message: string;
  is_read: boolean;
  created_at: string;
  sent_at: string | null;
};

export async function fetchAlertRules(): Promise<AlertRule[]> {
  const res = await fetch(`${API_BASE_URL}/alerts/rules/`, {
    headers: authHeaders(),
  });

  const dataRes = await parseResponse(res);
  if (!res.ok) throw new Error(JSON.stringify(dataRes));
  return dataRes;
}

export async function createAlertRule(data: {
  name: string;
  event_name?: string;
  metric?: string;
  operator: AlertOperator;
  threshold: number;
  time_window_minutes: number;
  enable_in_app?: boolean;
  enable_email?: boolean;
  email_to?: string;
  enable_webhook?: boolean;
  webhook_url?: string;
}): Promise<AlertRule> {
  const res = await fetch(`${API_BASE_URL}/alerts/rules/`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify(data),
  });

  const dataRes = await parseResponse(res);
  if (!res.ok) throw new Error(JSON.stringify(dataRes));
  return dataRes;
}

export async function updateAlertRule(
  id: number,
  data: Partial<AlertRule>
): Promise<AlertRule> {
  const res = await fetch(`${API_BASE_URL}/alerts/rules/${id}/`, {
    method: "PUT",
    headers: authHeaders(),
    body: JSON.stringify(data),
  });

  const dataRes = await parseResponse(res);
  if (!res.ok) throw new Error(JSON.stringify(dataRes));
  return dataRes;
}

export async function deleteAlertRule(id: number) {
  const res = await fetch(`${API_BASE_URL}/alerts/rules/${id}/`, {
    method: "DELETE",
    headers: authHeaders(),
  });

  const dataRes = await parseResponse(res);
  if (!res.ok) throw new Error(JSON.stringify(dataRes));
  return dataRes;
}

export async function evaluateAlertRule(id: number) {
  const res = await fetch(`${API_BASE_URL}/alerts/rules/${id}/evaluate/`, {
    method: "POST",
    headers: authHeaders(),
  });

  const dataRes = await parseResponse(res);
  if (!res.ok) throw new Error(JSON.stringify(dataRes));
  return dataRes;
}

export async function evaluateAllAlertRules() {
  const res = await fetch(`${API_BASE_URL}/alerts/rules/evaluate-all/`, {
    method: "POST",
    headers: authHeaders(),
  });

  const dataRes = await parseResponse(res);
  if (!res.ok) throw new Error(JSON.stringify(dataRes));
  return dataRes;
}

export async function muteAlertRule(id: number, minutes = 60): Promise<AlertRule> {
  const res = await fetch(`${API_BASE_URL}/alerts/rules/${id}/mute/`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ minutes }),
  });

  const dataRes = await parseResponse(res);
  if (!res.ok) throw new Error(JSON.stringify(dataRes));
  return dataRes;
}

export async function unmuteAlertRule(id: number): Promise<AlertRule> {
  const res = await fetch(`${API_BASE_URL}/alerts/rules/${id}/unmute/`, {
    method: "POST",
    headers: authHeaders(),
  });

  const dataRes = await parseResponse(res);
  if (!res.ok) throw new Error(JSON.stringify(dataRes));
  return dataRes;
}

export async function fetchAlertHistory(): Promise<AlertHistory[]> {
  const res = await fetch(`${API_BASE_URL}/alerts/history/`, {
    headers: authHeaders(),
  });

  const dataRes = await parseResponse(res);
  if (!res.ok) throw new Error(JSON.stringify(dataRes));
  return dataRes;
}

export async function fetchNotifications(): Promise<NotificationItem[]> {
  const res = await fetch(`${API_BASE_URL}/alerts/notifications/`, {
    headers: authHeaders(),
  });

  const dataRes = await parseResponse(res);
  if (!res.ok) throw new Error(JSON.stringify(dataRes));
  return dataRes;
}

export type ReportFrequency = "daily" | "weekly" | "monthly";
export type ReportFormat = "pdf" | "png";
export type ReportStatus = "pending" | "success" | "failed";

export type ScheduledReport = {
  id: number;
  dashboard: number;
  dashboard_name: string;
  name: string;
  frequency: ReportFrequency;
  report_format: ReportFormat;
  recipients: string;
  is_active: boolean;
  next_run_at: string;
  last_run_at: string | null;
  created_at: string;
  updated_at: string;
};

export type ReportHistory = {
  id: number;
  scheduled_report: number | null;
  dashboard: number;
  dashboard_name: string;
  report_name: string;
  report_format: ReportFormat;
  file_url: string | null;
  status: ReportStatus;
  error_message: string;
  generated_at: string;
};

export async function fetchScheduledReports(): Promise<ScheduledReport[]> {
  const res = await fetch(`${API_BASE_URL}/reports/scheduled/`, {
    headers: authHeaders(),
  });

  const dataRes = await parseResponse(res);
  if (!res.ok) throw new Error(JSON.stringify(dataRes));
  return dataRes;
}

export async function createScheduledReport(data: {
  dashboard: number;
  name: string;
  frequency: ReportFrequency;
  report_format: ReportFormat;
  recipients?: string;
  is_active?: boolean;
  next_run_at: string;
}): Promise<ScheduledReport> {
  const res = await fetch(`${API_BASE_URL}/reports/scheduled/`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify(data),
  });

  const dataRes = await parseResponse(res);
  if (!res.ok) throw new Error(JSON.stringify(dataRes));
  return dataRes;
}

export async function updateScheduledReport(
  id: number,
  data: Partial<ScheduledReport>
): Promise<ScheduledReport> {
  const res = await fetch(`${API_BASE_URL}/reports/scheduled/${id}/`, {
    method: "PUT",
    headers: authHeaders(),
    body: JSON.stringify(data),
  });

  const dataRes = await parseResponse(res);
  if (!res.ok) throw new Error(JSON.stringify(dataRes));
  return dataRes;
}

export async function deleteScheduledReport(id: number) {
  const res = await fetch(`${API_BASE_URL}/reports/scheduled/${id}/`, {
    method: "DELETE",
    headers: authHeaders(),
  });

  const dataRes = await parseResponse(res);
  if (!res.ok) throw new Error(JSON.stringify(dataRes));
  return dataRes;
}

export async function runScheduledReportNow(id: number) {
  const res = await fetch(`${API_BASE_URL}/reports/scheduled/${id}/run_now/`, {
    method: "POST",
    headers: authHeaders(),
  });

  const dataRes = await parseResponse(res);
  if (!res.ok) throw new Error(JSON.stringify(dataRes));
  return dataRes;
}

export async function fetchReportHistory(): Promise<ReportHistory[]> {
  const res = await fetch(`${API_BASE_URL}/reports/history/`, {
    headers: authHeaders(),
  });

  const dataRes = await parseResponse(res);
  if (!res.ok) throw new Error(JSON.stringify(dataRes));
  return dataRes;
}

export function getReportDownloadUrl(historyId: number) {
  return `${API_BASE_URL}/reports/history/${historyId}/download/`;
}



export type LiveSocketStatus = "connecting" | "connected" | "disconnected" | "reconnecting" | "error";

export type LiveSocketMessage =
  | {
      type: "connection";
      status: "connected";
      message: string;
      organization_id: number;
    }
  | {
      type: "event_created" | "event_processed";
      event: EventItem;
    }
  | {
      type: "dashboard_refresh";
      reason: string;
      event_id?: number;
    }
  | {
      type: "alert_triggered";
      notification: {
        id: number;
        title?: string;
        message: string;
        is_read?: boolean;
        created_at?: string | null;
        alert_rule?: string | null;
      };
    }
  | {
      type: "pong";
    };

export function getLiveDashboardWebSocketUrl() {
  const token = getAccessToken();
  const wsBaseUrl = API_BASE_URL.replace("http://", "ws://").replace("https://", "wss://").replace("/api", "");
  return `${wsBaseUrl}/ws/live/?token=${token || ""}`;
}
