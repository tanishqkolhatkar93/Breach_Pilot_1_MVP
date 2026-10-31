import './globals.css';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <head suppressHydrationWarning>
        <title>AgentShield AI — Autonomous Agent Safety Red-Team Judge</title>
        <meta name="description" content="Attack. Evaluate. Protect. Before You Publish." />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </head>
      <body className="bg-[#0B0F19] text-[#F8FAFC] antialiased" suppressHydrationWarning>
        {children}
      </body>
    </html>
  );
}
