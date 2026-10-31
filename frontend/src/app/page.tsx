'use client';

import dynamic from 'next/dynamic';

const AgentShieldDashboard = dynamic(
  () => import('../components/AgentShieldDashboard'),
  { ssr: false }
);

export default function Home() {
  return (
    <main suppressHydrationWarning>
      <AgentShieldDashboard />
    </main>
  );
}
