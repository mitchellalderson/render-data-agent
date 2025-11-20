import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen flex items-center justify-center bg-black text-zinc-100">
      <div className="text-center space-y-4">
        <h1 className="text-xl font-semibold">Data Analyst Agent</h1>
        <p className="text-sm text-zinc-400">
          Go to the signup & ICP analysis workspace.
        </p>
        <Link
          href="/data-analyst"
          className="inline-flex items-center rounded-lg bg-zinc-100 text-black text-sm px-4 py-2 hover:bg-zinc-200"
        >
          Open workspace
        </Link>
      </div>
    </main>
  );
}
