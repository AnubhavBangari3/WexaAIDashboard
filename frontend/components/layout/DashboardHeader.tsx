import { logout, type User } from "../../lib/api";

export default function DashboardHeader({ user }: { user: User }) {
  return (
    <div className="mb-6 flex justify-between rounded-xl bg-white p-6 shadow">
      <div>
        <h1 className="text-3xl font-bold">Wexa AI Dashboard</h1>
        <p className="mt-2">Email: {user.email}</p>
        <p>
          Role: <b>{user.role}</b>
        </p>
        <p>
          Organization: <b>{user.organization_name}</b>
        </p>
      </div>

      <div className="flex gap-3">
        <button
          onClick={() => (window.location.href = "/alerts")}
          className="h-fit rounded bg-indigo-600 px-4 py-2 text-white"
        >
          Alerts
        </button>

        <button
          onClick={logout}
          className="h-fit rounded bg-red-600 px-4 py-2 text-white"
        >
          Logout
        </button>
      </div>
    </div>
  );
}
