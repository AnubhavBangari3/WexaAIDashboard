
"use client";

export default function InviteUserForm({
  canInvite,
  username,
  email,
  role,
  setUsername,
  setEmail,
  setRole,
  handleInvite,
}: {
  canInvite: boolean;
  username: string;
  email: string;
  role: "admin" | "analyst" | "viewer";
  setUsername: (value: string) => void;
  setEmail: (value: string) => void;
  setRole: (value: "admin" | "analyst" | "viewer") => void;
  handleInvite: (e: React.FormEvent) => Promise<void>;
}) {
  if (!canInvite) {
    return (
      <div className="rounded-xl bg-white p-6 shadow">
        Viewer/Analyst cannot invite users.
      </div>
    );
  }

  return (
    <form onSubmit={handleInvite} className="rounded-xl bg-white p-6 shadow">
      <h2 className="mb-4 text-xl font-bold">Invite User</h2>

      <input
        className="mb-4 w-full rounded border p-3"
        placeholder="Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />

      <input
        className="mb-4 w-full rounded border p-3"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />

      <select
        className="mb-4 w-full rounded border p-3"
        value={role}
        onChange={(e) =>
          setRole(e.target.value as "admin" | "analyst" | "viewer")
        }
      >
        <option value="admin">Admin</option>
        <option value="analyst">Analyst</option>
        <option value="viewer">Viewer</option>
      </select>

      <button className="rounded bg-blue-600 px-5 py-3 text-white">
        Invite User
      </button>
    </form>
  );
}
