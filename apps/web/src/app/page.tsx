import type { Metadata } from "next";
import { redirect } from "next/navigation";

export default function RootPage() {
  redirect(`/${process.env.SN_DEFAULT_INDUSTRY ?? "legal"}`);
}

export const metadata: Metadata = {
  robots: { index: false, follow: false },
};
