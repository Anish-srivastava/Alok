import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Face Recognition System",
  description: "Attendance System using facial recognition technology",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link rel="icon" href="/favicon.png" />
      </head>
      <body className="bg-gradient-to-br from-slate-50 via-white to-blue-50 min-h-screen">
        {children}
      </body>
    </html>
  );
}
