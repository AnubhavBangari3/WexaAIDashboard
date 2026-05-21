export default function MessageBanner({ message }: { message: string }) {
  if (!message) return null;

  return (
    <div className="mb-6 rounded-xl bg-yellow-100 p-4 font-semibold text-yellow-900">
      {message}
    </div>
  );
}
