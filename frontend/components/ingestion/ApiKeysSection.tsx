import type { ApiKey } from "../../lib/api";

export default function ApiKeysSection({ apiKeys }: { apiKeys: ApiKey[] }) {
  return (
    <section className="mb-6 rounded-xl bg-white p-6 shadow">
      <h2 className="mb-4 text-xl font-bold">API Keys</h2>

      {apiKeys.length === 0 ? (
        <p>No API keys created yet.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full border text-left text-sm">
            <thead className="bg-gray-100">
              <tr>
                <th className="border p-3">Name</th>
                <th className="border p-3">Key</th>
                <th className="border p-3">Active</th>
              </tr>
            </thead>
            <tbody>
              {apiKeys.map((key) => (
                <tr key={key.id}>
                  <td className="border p-3">{key.name}</td>
                  <td className="border p-3 font-mono">{key.key}</td>
                  <td className="border p-3">{key.is_active ? "Yes" : "No"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
