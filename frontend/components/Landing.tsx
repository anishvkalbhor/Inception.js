"use client";

import React from "react";
import Link from "next/link";
import ThemeToggle from "./ThemeToggle";
import { useTheme } from "@/lib/ThemeContext";

// ========================= SVG Icon Components =========================
const Icon = {
  Search: () => (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="h-8 w-8 text-cyan-400"
    >
      <circle cx="11" cy="11" r="8" />
      <line x1="21" y1="21" x2="16.65" y2="16.65" />
    </svg>
  ),

  Zap: () => (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="h-8 w-8 text-cyan-400"
    >
      <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
    </svg>
  ),

  ShieldCheck: () => (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="h-8 w-8 text-cyan-400"
    >
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
      <path d="m9 12 2 2 4-4" />
    </svg>
  ),

  Bot: () => (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="h-8 w-8 mb-4 text-cyan-400"
    >
      <path d="M12 8V4H8" />
      <rect x="4" y="12" width="16" height="8" rx="2" />
      <path d="M2 12h2" />
      <path d="M20 12h2" />
      <path d="M12 12v.01" />
    </svg>
  ),
};

// ========================= Landing Page Component =========================
export default function Landing() {
  const { theme } = useTheme();

  const isDark = theme === "dark";
  const headerBgClass = isDark ? "bg-neutral-900/50 border-neutral-800" : "bg-gray-50/50 border-gray-200";

  return (
    <div className={`min-h-screen w-full ${isDark ? "bg-neutral-950 text-white" : "bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 text-gray-900"} overflow-x-hidden transition-colors duration-300`}>
      {isDark ? (
        <div className="absolute top-0 z-[-2] h-screen w-screen bg-neutral-950 bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(120,119,198,0.3),rgba(255,255,255,0))]" />
      ) : (
        <div className="absolute top-0 z-[-2] h-full w-full bg-gradient-to-br from-blue-100 via-indigo-50 to-purple-100 opacity-40" />
      )}

      {/* Header with Navigation - Same style as search page */}
      <header className={`border-b ${headerBgClass} backdrop-blur sticky top-0 z-50`}>
        <div className="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center">
          <div>
            <h1 className={`text-2xl font-bold ${isDark ? "text-cyan-400" : "text-blue-600"}`}>Victor</h1>
            <p className={`text-xs ${isDark ? "text-gray-500" : "text-gray-600"} mt-1`}>AI-Powered Document Search</p>
          </div>
          <div className="flex gap-3 items-center">
            <ThemeToggle />
            <Link
              href="/upload"
              className={`px-6 py-2 rounded-lg transition-colors font-medium border ${
                isDark
                  ? "bg-neutral-800 hover:bg-neutral-700 text-gray-300 border-neutral-700"
                  : "bg-gray-200 hover:bg-gray-300 text-gray-700 border-gray-300"
              }`}
            >
              📤 Upload PDF
            </Link>
            <Link
              href="/search"
              className={`px-6 py-2 rounded-lg transition-colors font-medium ${
                isDark
                  ? "bg-cyan-600 hover:bg-cyan-700 text-white"
                  : "bg-blue-600 hover:bg-blue-700 text-white"
              }`}
            >
              🔍 Try Victor
            </Link>
          </div>
        </div>
      </header>

      <main>
        {/* ========================= Hero Section ========================= */}
        <section className="relative z-10 flex flex-col items-center justify-center min-h-[calc(100vh-80px)] px-4 text-center">
          {/* Animated background elements */}
          {isDark && (
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
              <div className="absolute top-20 left-10 w-72 h-72 bg-cyan-500 rounded-full mix-blend-screen filter blur-3xl opacity-20 animate-blob" />
              <div className="absolute top-40 right-10 w-72 h-72 bg-purple-500 rounded-full mix-blend-screen filter blur-3xl opacity-20 animate-blob animation-delay-2000" />
              <div className="absolute -bottom-8 left-1/2 w-72 h-72 bg-blue-500 rounded-full mix-blend-screen filter blur-3xl opacity-20 animate-blob animation-delay-4000" />
            </div>
          )}

          <h1 className={`relative text-6xl md:text-7xl lg:text-8xl font-black uppercase leading-tight bg-clip-text text-transparent mb-4 ${
            isDark
              ? "bg-gradient-to-b from-white via-cyan-200 to-cyan-400"
              : "bg-gradient-to-b from-blue-900 via-blue-600 to-blue-500"
          }`}>
            Navigate Complexity
          </h1>
          <h2 className={`relative text-4xl md:text-5xl lg:text-6xl font-bold uppercase bg-clip-text text-transparent mb-8 ${
            isDark
              ? "bg-gradient-to-r from-emerald-400 via-cyan-400 to-blue-400"
              : "bg-gradient-to-r from-green-600 via-blue-600 to-blue-500"
          }`}>
            Efficient. Fast Retrieval.
          </h2>

          <p className={`relative max-w-3xl text-lg mb-16 leading-relaxed ${
            isDark ? "text-gray-300" : "text-gray-700"
          }`}>
            Transform vast regulatory databases into an intelligent, queryable knowledge base. Get instant answers backed by verified sources.
          </p>

          <div className="relative flex gap-4 flex-wrap justify-center">
            <Link
              href="/search"
              className="inline-flex items-center justify-center px-10 py-4 font-mono font-medium tracking-tighter text-white bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-700 hover:to-blue-700 rounded-lg transition-all transform hover:scale-105 shadow-lg hover:shadow-cyan-500/50"
            >
              🔍 Search Documents
            </Link>
            <Link
              href="/upload"
              className="inline-flex items-center justify-center px-10 py-4 font-mono font-medium tracking-tighter text-cyan-400 bg-neutral-900/50 hover:bg-neutral-900 rounded-lg transition-all border border-cyan-600/50 hover:border-cyan-400 transform hover:scale-105"
            >
              📤 Upload PDFs
            </Link>
          </div>
        </section>

        {/* ========================= About Section ========================= */}
        <section id="about" className="py-20 px-4 relative z-10">
          <div className="max-w-6xl mx-auto">
            <h2 className="text-4xl font-bold mb-8 text-center">About Victor</h2>
            <div className="max-w-4xl mx-auto bg-gradient-to-br from-neutral-900/50 to-neutral-950/50 border border-cyan-600/20 rounded-lg p-8 hover:border-cyan-600/50 transition-all hover:shadow-lg hover:shadow-cyan-600/10">
              <p className="text-gray-300 leading-relaxed text-lg">
                Victor is an advanced AI-powered information retrieval tool designed specifically for navigating the complex web of government regulations, policies, and schemes. Our mission is to empower decision-makers by transforming vast, unstructured databases into an intelligent, queryable knowledge base. By leveraging state-of-the-art technologies, Victor provides instant, accurate, and verifiable answers, fostering a new era of efficiency and data-driven governance.
              </p>
            </div>
          </div>
        </section>

        {/* ========================= Features ========================= */}
        <section id="features" className="py-20 px-4">
          <div className="max-w-6xl mx-auto">
            <h2 className="text-4xl font-bold mb-4 text-center">The Future of Information Retrieval</h2>
            <p className="text-gray-400 max-w-3xl mx-auto mb-16 text-center">
              Victor transforms how you interact with vast regulatory databases, providing unparalleled speed, accuracy, and trust.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
              {[
                {
                  icon: <Icon.Zap />,
                  title: "Instant Retrieval",
                  desc: "Ask questions in plain English and get answers in seconds, not hours.",
                },
                {
                  icon: <Icon.ShieldCheck />,
                  title: "Verifiable Sources",
                  desc: "Every answer is backed by direct citations to the original source document.",
                },
                {
                  icon: <Icon.Search />,
                  title: "Hybrid Search",
                  desc: "Combines semantic and keyword search for unparalleled accuracy.",
                },
                {
                  icon: <Icon.Bot />,
                  title: "Advanced AI Models",
                  desc: "Utilizes state-of-the-art LLMs to synthesize clear, concise answers.",
                },
              ].map(({ icon, title, desc }) => (
                <div
                  key={title}
                  className="feature-card flex flex-col items-center text-center p-8 rounded-lg border border-neutral-700 hover:border-cyan-600/50 transition-all duration-300"
                >
                  <div className="mb-4">{icon}</div>
                  <h3 className="text-xl font-semibold mb-2 text-cyan-400">{title}</h3>
                  <p className="text-gray-400 text-sm">{desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ========================= Metrics ========================= */}
        <section className="py-20 px-4 bg-neutral-900/30 relative z-10">
          <div className="max-w-6xl mx-auto">
            <h2 className="text-4xl font-bold mb-12 text-center">Prototype Testing Results</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {[
                {
                  value: "30+",
                  label: "Documents Indexed",
                  icon: "📚",
                },
                {
                  value: "99%",
                  label: "Retrieval Accuracy",
                  icon: "🎯",
                },
                {
                  value: "95%",
                  label: "Reduction in Research Time",
                  icon: "⚡",
                },
              ].map(({ value, label, icon }) => (
                <div
                  key={label}
                  className="p-8 bg-gradient-to-br from-neutral-800/50 to-neutral-900/50 border border-cyan-600/30 rounded-lg hover:border-cyan-600/70 transition-all hover:shadow-lg hover:shadow-cyan-600/10 text-center group"
                >
                  <div className="text-5xl mb-4 group-hover:scale-110 transition-transform">{icon}</div>
                  <h3 className="text-5xl font-bold text-cyan-400 mb-2">{value}</h3>
                  <p className="text-gray-400">{label}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ========================= Upload Section ========================= */}
        <section className="py-20 px-4 border-t border-neutral-800">
          <div className="max-w-6xl mx-auto">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
              <div>
                <h2 className="text-4xl font-bold mb-6">Upload Your Documents</h2>
                <p className="text-gray-400 text-lg mb-8">
                  Start by uploading your PDF documents. Victor will automatically process and index them, making them instantly searchable with AI-powered queries.
                </p>
                <div className="space-y-4">
                  <div className="flex gap-3">
                    <span className="text-cyan-400 text-2xl">✓</span>
                    <div>
                      <h4 className="text-lg font-semibold mb-1">Multiple Formats</h4>
                      <p className="text-gray-500 text-sm">Support for PDF and document formats</p>
                    </div>
                  </div>
                  <div className="flex gap-3">
                    <span className="text-cyan-400 text-2xl">✓</span>
                    <div>
                      <h4 className="text-lg font-semibold mb-1">Instant Indexing</h4>
                      <p className="text-gray-500 text-sm">Fast processing with vector embeddings</p>
                    </div>
                  </div>
                  <div className="flex gap-3">
                    <span className="text-cyan-400 text-2xl">✓</span>
                    <div>
                      <h4 className="text-lg font-semibold mb-1">Secure Storage</h4>
                      <p className="text-gray-500 text-sm">Your documents are encrypted and safe</p>
                    </div>
                  </div>
                </div>
                <Link
                  href="/upload"
                  className="inline-flex items-center justify-center mt-8 px-10 py-4 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg font-medium transition-colors"
                >
                  📤 Upload Documents Now
                </Link>
              </div>
              <div className="bg-neutral-900/30 border border-neutral-700 rounded-lg p-12 text-center">
                <div className="text-6xl mb-4">📄</div>
                <h3 className="text-2xl font-bold mb-4">Upload & Index</h3>
                <p className="text-gray-400 mb-8">
                  Drag and drop your documents or click to browse
                </p>
                <div className="bg-neutral-950/50 rounded border-2 border-dashed border-neutral-600 p-8">
                  <p className="text-gray-500">PDF files, Word documents, and more</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ========================= CTA Section ========================= */}
        <section className="py-20 px-4 border-t border-neutral-800">
          <div className="max-w-6xl mx-auto text-center">
            <h2 className="text-4xl font-bold mb-6">Ready to Transform Your Research?</h2>
            <p className="text-gray-400 mb-8 max-w-2xl mx-auto">
              Upload your documents and start searching with Victor's AI-powered retrieval system today.
            </p>
            <div className="flex gap-4 justify-center">
              <Link
                href="/upload"
                className="inline-flex items-center justify-center px-10 py-4 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg font-medium transition-colors"
              >
                📤 Upload Documents
              </Link>
              <Link
                href="/search"
                className="inline-flex items-center justify-center px-10 py-4 bg-neutral-800 hover:bg-neutral-700 text-gray-300 rounded-lg font-medium transition-colors border border-neutral-700"
              >
                🔍 Search Now
              </Link>
            </div>
          </div>
        </section>
      </main>

      {/* ========================= Footer ========================= */}
      <footer className="border-t border-neutral-800 bg-neutral-900/50 mt-20">
        <div className="max-w-6xl mx-auto px-6 py-12">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
            <div>
              <h3 className="text-xl font-bold text-cyan-400">Victor</h3>
              <p className="text-gray-500 mt-2 text-sm">AI-Powered Information Retrieval</p>
            </div>

            {[
              {
                title: "Product",
                links: ["Features", "Search", "Documentation"],
              },
              {
                title: "Company",
                links: ["About Us", "Contact"],
              },
              {
                title: "Legal",
                links: ["Privacy Policy", "Terms of Service"],
              },
            ].map(({ title, links }) => (
              <div key={title}>
                <h4 className="font-semibold mb-4 text-gray-300">{title}</h4>
                <ul className="space-y-2">
                  {links.map((link) => (
                    <li key={link}>
                      <a href="#" className="text-gray-500 hover:text-cyan-400 text-sm transition-colors">
                        {link}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          <div className="text-center py-6 text-gray-500 text-sm border-t border-neutral-800">
            © 2025 Victor. All Rights Reserved. | Powered by Milvus & OpenRouter
          </div>
        </div>
      </footer>

      {/* ========================= Styles ========================= */}
      <style jsx global>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;900&display=swap');

        html {
          scroll-behavior: smooth;
        }

        body {
          margin: 0;
          padding: 0;
          overflow-x: hidden;
          font-family: 'Inter', sans-serif;
        }

        @keyframes blob {
          0%, 100% {
            transform: translate(0, 0) scale(1);
          }
          33% {
            transform: translate(30px, -50px) scale(1.1);
          }
          66% {
            transform: translate(-20px, 20px) scale(0.9);
          }
        }

        .animate-blob {
          animation: blob 7s infinite;
        }

        .animation-delay-2000 {
          animation-delay: 2s;
        }

        .animation-delay-4000 {
          animation-delay: 4s;
        }

        .feature-card {
          background: linear-gradient(145deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0));
          transition: all 0.3s ease;
          position: relative;
          overflow: hidden;
        }

        .feature-card:before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: radial-gradient(circle at 50% 0%, rgba(0, 255, 255, 0.2), transparent 70%);
          opacity: 0;
          transition: opacity 0.3s ease;
          transform: translateY(100%);
        }

        .feature-card:hover {
          transform: translateY(-5px);
          border-color: rgba(0, 255, 255, 0.3) !important;
          box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        }

        .feature-card:hover:before {
          opacity: 1;
          transform: translateY(0);
        }
      `}</style>
    </div>
  );
}
