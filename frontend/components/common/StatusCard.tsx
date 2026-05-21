export default function StatusCard({ title, value }: { title: string; value: string }) {
  return (
    <div className="rounded-xl bg-white p-5 shadow">
      <p className="text-gray-500">{title}</p>
      <h2 className="mt-2 text-xl font-bold">{value}</h2>
    </div>
  );
}
