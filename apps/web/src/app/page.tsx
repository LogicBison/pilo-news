import type { Metadata } from "next";

import { LobbyPage, lobbyMetadata } from "@/components/lobby/LobbyPage";

// The apex lobby is the network's front door: it lists every desk and sells the
// two services. Request-scoped (the desk links depend on the host), so it is
// rendered per request with the API response cached for five minutes.
export const dynamic = "force-dynamic";

export function generateMetadata(): Promise<Metadata> {
  return lobbyMetadata("en");
}

export default function RootPage() {
  return <LobbyPage locale="en" />;
}
