export default function HomePage() {
  const env = process.env.APP_ENV ?? "dev";

  return (
    <main className="mx-auto flex min-h-screen max-w-3xl flex-col justify-center gap-6 p-8">
      <p className="text-sm uppercase tracking-widest text-gray-500">
        {env} environment
      </p>
      <h1 className="text-4xl font-semibold tracking-tight">System News</h1>
      <p className="max-w-xl text-lg text-gray-600">
        Industry news, in your language. The channel sites and the public API
        land in M5-M6; this scaffold proves the stack boots in both dev and prd.
      </p>
      <p className="text-sm text-gray-500">
        API health: <code>http://localhost:8080/v1/health</code>
      </p>
    </main>
  );
}
