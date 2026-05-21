import type { EventItem } from "../../lib/api";

export default function EventsTable({ events }: { events: EventItem[] }) {
  return (
    <section className="mb-6 rounded-xl bg-white p-6 shadow">
      <h2 className="mb-4 text-xl font-bold">Events</h2>

      {events.length === 0 ? (
        <p>No events found. Click Test Single Event.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full border text-left text-sm">
            <thead className="bg-gray-100">
              <tr>
                <th className="border p-3">ID</th>
                <th className="border p-3">Event</th>
                <th className="border p-3">Source</th>
                <th className="border p-3">Status</th>
                <th className="border p-3">Payload</th>
              </tr>
            </thead>
            <tbody>
              {events.map((event) => (
                <tr key={event.id}>
                  <td className="border p-3">{event.id}</td>
                  <td className="border p-3 font-semibold">
                    {event.event_name}
                  </td>
                  <td className="border p-3">{event.source_type}</td>
                  <td className="border p-3">
                    <span
                      className={`rounded px-2 py-1 text-xs font-bold ${
                        event.status === "processed"
                          ? "bg-green-100 text-green-700"
                          : event.status === "failed"
                          ? "bg-red-100 text-red-700"
                          : "bg-yellow-100 text-yellow-700"
                      }`}
                    >
                      {event.status}
                    </span>
                  </td>
                  <td className="border p-3">
                    <pre className="max-w-xs overflow-auto text-xs">
                      {JSON.stringify(event.payload, null, 2)}
                    </pre>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
