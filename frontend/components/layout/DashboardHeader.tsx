import { logout, type User } from "../../lib/api";

export default function DashboardHeader({ user }: { user: User }) {
  return (
    <div className="mb-6 flex flex-col gap-4 rounded-2xl bg-white p-5 shadow md:flex-row md:items-start md:justify-between">
      <div className="min-w-0 flex-1">
        <h1 className="break-words text-3xl font-bold leading-tight md:text-5xl">
          Wexa AI Dashboard
        </h1>

        <div className="mt-4 space-y-1 text-sm md:text-base">
          <p className="break-all">
            Email: <span className="font-medium">{user.email}</span>
          </p>

          <p>
            Role: <b>{user.role}</b>
          </p>

          <p className="break-words">
            Organization: <b>{user.organization_name}</b>
          </p>
        </div>
      </div>

      <div className="flex w-full flex-col gap-3 sm:flex-row md:w-auto">
        <button
          onClick={() => (window.location.href = "/alerts")}
          className="rounded-xl bg-indigo-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-indigo-700"
        >
          Alerts
        </button>

        <button
          onClick={logout}
          className="rounded-xl bg-red-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-red-700"
        >
          Logout
        </button>
      </div>
    </div>
  );
}