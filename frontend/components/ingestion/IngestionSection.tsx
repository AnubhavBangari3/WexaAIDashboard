"use client";

import type { ApiKey } from "../../lib/api";

export default function IngestionSection({
  apiKeys,
  selectedFile,
  canManageApiKeys,
  setSelectedFile,
  setMessage,
  runAction,
  ingestSingleEventAction,
  ingestBatchEventsAction,
  createApiKeyAction,
  uploadCsvAction,
  testWebhookAction,
  loadData,
}: {
  apiKeys: ApiKey[];
  selectedFile: File | null;
  canManageApiKeys: boolean;
  setSelectedFile: (file: File | null) => void;
  setMessage: (message: string) => void;
  runAction: (action: () => Promise<unknown>, successMessage: string) => Promise<void>;
  ingestSingleEventAction: () => Promise<unknown>;
  ingestBatchEventsAction: () => Promise<unknown>;
  createApiKeyAction: () => Promise<unknown>;
  uploadCsvAction: (file: File) => Promise<unknown>;
  testWebhookAction: (apiKey: string) => Promise<unknown>;
  loadData: () => Promise<void>;
}) {
  return (
    <section className="mb-6 rounded-xl bg-white p-6 shadow">
      <h2 className="mb-4 text-2xl font-bold">Data Ingestion & Sources</h2>

      <div className="grid grid-cols-1 gap-3 md:grid-cols-4">
        <button
          onClick={() =>
            runAction(ingestSingleEventAction, "Single event ingested successfully")
          }
          className="rounded bg-blue-600 px-4 py-3 text-white"
        >
          Test Single Event
        </button>

        <button
          onClick={() =>
            runAction(ingestBatchEventsAction, "Batch events ingested successfully")
          }
          className="rounded bg-green-600 px-4 py-3 text-white"
        >
          Test Batch Event
        </button>

        <button
          onClick={() =>
            runAction(createApiKeyAction, "API key created successfully")
          }
          disabled={!canManageApiKeys}
          className="rounded bg-purple-600 px-4 py-3 text-white disabled:bg-gray-400"
        >
          Create API Key
        </button>

        <button
          onClick={() => loadData()}
          className="rounded bg-gray-800 px-4 py-3 text-white"
        >
          Refresh Events
        </button>
      </div>

      <div className="mt-5 rounded-lg border p-4">
        <h3 className="mb-3 font-bold">CSV Upload Test</h3>

        <input
          type="file"
          accept=".csv"
          onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
          className="mb-3 block w-full rounded border p-2"
        />

        <button
          onClick={() => {
            if (!selectedFile) {
              setMessage("Please select a CSV file first");
              return;
            }

            runAction(
              () => uploadCsvAction(selectedFile),
              "CSV uploaded and events created successfully"
            );
          }}
          className="rounded bg-orange-600 px-4 py-2 text-white"
        >
          Upload CSV
        </button>
      </div>

      <div className="mt-5 rounded-lg border p-4">
        <h3 className="mb-3 font-bold">Webhook Test</h3>

        {apiKeys.length === 0 ? (
          <p className="text-gray-600">
            Create API key first, then test webhook.
          </p>
        ) : (
          <button
            onClick={() =>
              runAction(
                () => testWebhookAction(apiKeys[0].key),
                "Webhook event ingested successfully"
              )
            }
            className="rounded bg-pink-600 px-4 py-2 text-white"
          >
            Test Webhook With Latest API Key
          </button>
        )}
      </div>
    </section>
  );
}
