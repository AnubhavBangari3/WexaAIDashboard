"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { Widget, WidgetData } from "../../lib/api";

export default function WidgetCard({
  widget,
  data,
  onTimeRangeChange,
}: {
  widget: Widget;
  data?: WidgetData;
  onTimeRangeChange: (
    widget: Widget,
    range: "24h" | "7d" | "30d"
  ) => Promise<void>;
}) {
  const chartData = data?.data || [];

  return (
    <div
      className={`rounded-xl bg-white p-5 shadow ${
        widget.widget_type === "kpi" ? "lg:col-span-1" : "lg:col-span-1"
      }`}
    >
      <div className="mb-4 flex items-center justify-between gap-3">
        <div>
          <h3 className="text-lg font-bold">{widget.title}</h3>
          <p className="text-xs text-gray-500">
            Type: {widget.widget_type.toUpperCase()}
          </p>
        </div>

        <select
          value={widget.time_range}
          onChange={(e) =>
            onTimeRangeChange(widget, e.target.value as "24h" | "7d" | "30d")
          }
          className="rounded border p-2 text-sm"
        >
          <option value="24h">24h</option>
          <option value="7d">7d</option>
          <option value="30d">30d</option>
        </select>
      </div>

      {widget.widget_type === "kpi" && (
        <div className="rounded-lg bg-gray-50 p-8">
          <p className="text-sm text-gray-500">Value</p>
          <h2 className="mt-2 text-5xl font-bold">{data?.value ?? 0}</h2>
        </div>
      )}

      {widget.widget_type === "line" && (
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="value" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {widget.widget_type === "bar" && (
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {widget.widget_type === "pie" && (
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Tooltip />
              <Pie
                data={chartData}
                dataKey="value"
                nameKey="name"
                outerRadius={90}
                label
              >
                {chartData.map((_, index) => (
                  <Cell key={index} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
        </div>
      )}

      {widget.widget_type === "table" && (
        <div className="overflow-x-auto">
          <table className="w-full border text-left text-sm">
            <thead className="bg-gray-100">
              <tr>
                <th className="border p-2">Name</th>
                <th className="border p-2">Value</th>
              </tr>
            </thead>
            <tbody>
              {chartData.map((row) => (
                <tr key={row.name}>
                  <td className="border p-2">{row.name}</td>
                  <td className="border p-2">{row.value}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
