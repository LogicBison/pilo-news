import type { Metadata } from "next";
import { redirect } from "next/navigation";

// Runtime: SN_DEFAULT_INDUSTRY is read per request so switching the industry
// needs only an env change + container restart, never a rebuild.
export const dynamic = "force-dynamic";

export default function RootPage() {
  redirect(`/${process.env.SN_DEFAULT_INDUSTRY ?? "legal"}`);
}

export const metadata: Metadata = {
  robots: { index: false, follow: false },
};
