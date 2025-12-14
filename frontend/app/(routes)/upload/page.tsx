"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import ThemeToggle from "@/components/ThemeToggle";

const PIPELINE_STEPS = [
  "Uploaded",
  "Parsing document",
  "Chunking content",
  "Generating embeddings",
  "Indexing in search",
  "Ready to query"
];

interface DocumentInfo {
  document_id: string;
  version: number;
  status: string;
  progress_step?: number;
  ready?: boolean;
  filename?: string;
}

export default function Upload() {
  const router = useRouter();

  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState("");
  const [documents, setDocuments] = useState<Map<string, DocumentInfo>>(new Map());
  const [uploadProgress, setUploadProgress] = useState<Map<string, number>>(new Map());
  const [isDragging, setIsDragging] = useState(false);

  // 🔁 Poll pipeline status for all documents
  useEffect(() => {
    if (documents.size === 0) return;

    const intervals: NodeJS.Timeout[] = [];
    let redirectScheduled = false;

    documents.forEach((docInfo, docId) => {
      // Skip if already ready
      if (docInfo.ready) return;

      const interval = setInterval(async () => {
        try {
          const res = await fetch(
            `http://localhost:8000/api/upload/${docId}/status?version=${docInfo.version}`
          );
          
          if (!res.ok) {
            console.error(`Status check failed for ${docId}`);
            return;
          }

          const data = await res.json();
          
          setDocuments(prev => {
            const updated = new Map(prev);
            const current = updated.get(docId);
            if (current) {
              updated.set(docId, {
                ...current,
                progress_step: data.progress_step ?? 0,
                ready: data.ready ?? false,
                status: data.stage || current.status
              });
            }
            
            // Check if all documents are ready
            const allReady = Array.from(updated.values()).every(doc => doc.ready);
            if (allReady && updated.size > 0 && !redirectScheduled) {
              redirectScheduled = true;
              setTimeout(() => {
                router.push("/chat");
              }, 2000);
            }
            
            return updated;
          });
        } catch (e) {
          console.error(`Status polling failed for ${docId}:`, e);
        }
      }, 2000);

      intervals.push(interval);
    });

    return () => {
      intervals.forEach(interval => clearInterval(interval));
    };
  }, [documents, router]);

  const handleFiles = useCallback(async (files: FileList | null) => {
    if (!files || files.length === 0) return;

    setUploading(true);
    setMessage("");
    setDocuments(new Map());
    setUploadProgress(new Map());

    const fileArray = Array.from(files);
    let successCount = 0;
    let failCount = 0;

    // Upload all files concurrently
    const uploadPromises = fileArray.map(async (file) => {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("org_id", "TEMP_ORG");
      formData.append("uploader_id", "TEMP_USER");
      formData.append("category", "uploads");

      try {
        // Simulate upload progress
        const progressInterval = setInterval(() => {
          setUploadProgress(prev => {
            const updated = new Map(prev);
            const current = updated.get(file.name) || 0;
            if (current < 90) {
              updated.set(file.name, current + 10);
            }
            return updated;
          });
        }, 200);

        const res = await fetch("http://localhost:8000/api/upload/", {
          method: "POST",
          body: formData
        });

        clearInterval(progressInterval);

        if (!res.ok) {
          throw new Error(`Upload failed for ${file.name}`);
        }

        const data = await res.json();
        
        setUploadProgress(prev => {
          const updated = new Map(prev);
          updated.set(file.name, 100);
          return updated;
        });
        
        setDocuments(prev => {
          const updated = new Map(prev);
          updated.set(data.document_id, {
            document_id: data.document_id,
            version: data.version,
            status: data.status,
            progress_step: 0,
            ready: false,
            filename: file.name
          });
          return updated;
        });

        successCount++;
        return { success: true, file: file.name, data };
      } catch (err) {
        console.error(`Error uploading ${file.name}:`, err);
        failCount++;
        return { success: false, file: file.name, error: err };
      }
    });

    await Promise.all(uploadPromises);

    setUploading(false);
    
    if (successCount > 0) {
      setMessage(
        `Successfully uploaded ${successCount} file${successCount > 1 ? 's' : ''}. ` +
        (failCount > 0 ? `${failCount} failed.` : "Processing started.")
      );
    } else {
      setMessage("All uploads failed. Please try again.");
    }
  }, []);

  const handleUpload = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    handleFiles(e.target.files);
    e.target.value = "";
  }, [handleFiles]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    handleFiles(e.dataTransfer.files);
  }, [handleFiles]);

  const allReady = Array.from(documents.values()).every(doc => doc.ready);
  const documentsArray = Array.from(documents.entries());
  const totalProgress = documentsArray.length > 0
    ? documentsArray.reduce((sum, [, doc]) => sum + (doc.progress_step ?? 0), 0) / documentsArray.length
    : 0;

  return (
    <main className="min-h-screen bg-gradient-to-br from-black via-neutral-900 to-black text-white">
      {/* NAV */}
      <nav className="flex justify-between items-center px-8 py-6 border-b border-neutral-800/50 backdrop-blur-sm bg-black/30">
        <Link href="/" className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
          Victor
        </Link>
        <ThemeToggle />
      </nav>

      <section className="max-w-4xl mx-auto px-8 py-16 space-y-8">
        <header className="text-center space-y-4 animate-fade-in">
          <h1 className="text-5xl md:text-6xl font-bold bg-gradient-to-r from-white via-blue-100 to-purple-100 bg-clip-text text-transparent">
            Upload Documents
          </h1>
          <p className="text-gray-400 text-lg">
            Upload one or multiple PDF documents. Victor will parse, understand, and index them automatically.
          </p>
        </header>

        {/* Upload Box with Drag & Drop */}
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`
            relative border-2 border-dashed rounded-2xl p-12 text-center space-y-6
            transition-all duration-300 ease-in-out
            ${isDragging 
              ? 'border-blue-400 bg-blue-500/10 scale-[1.02] shadow-2xl shadow-blue-500/20' 
              : 'border-neutral-700 bg-neutral-900/50 hover:border-neutral-600 hover:bg-neutral-900/70'
            }
            ${uploading ? 'pointer-events-none opacity-75' : 'cursor-pointer'}
          `}
        >
          <input
            type="file"
            multiple
            accept=".pdf"
            onChange={handleUpload}
            disabled={uploading}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
            id="file-upload"
          />

          <div className="space-y-4">
            <div className="flex justify-center">
              <div className={`
                w-20 h-20 rounded-full flex items-center justify-center
                transition-all duration-300
                ${isDragging 
                  ? 'bg-blue-500/20 scale-110' 
                  : 'bg-neutral-800/50'
                }
              `}>
                <svg
                  className={`w-10 h-10 transition-all duration-300 ${isDragging ? 'text-blue-400 scale-110' : 'text-neutral-400'}`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                  />
                </svg>
              </div>
            </div>

            <div>
              <p className="text-xl font-semibold text-white mb-2">
                {isDragging ? "Drop files here" : "Drag & drop files here"}
              </p>
              <p className="text-sm text-gray-400">
                or <label htmlFor="file-upload" className="text-blue-400 hover:text-blue-300 cursor-pointer underline">browse</label> to select files
              </p>
              <p className="text-xs text-gray-500 mt-2">Supports PDF files only</p>
            </div>
          </div>

          {uploading && (
            <div className="absolute inset-0 bg-black/50 backdrop-blur-sm rounded-2xl flex items-center justify-center">
              <div className="text-center space-y-4">
                <div className="relative w-16 h-16 mx-auto">
                  <div className="absolute inset-0 border-4 border-blue-500/20 rounded-full"></div>
                  <div className="absolute inset-0 border-4 border-transparent border-t-blue-500 rounded-full animate-spin"></div>
                </div>
                <p className="text-blue-400 font-semibold animate-pulse">
                  Uploading {documents.size} file{documents.size !== 1 ? 's' : ''}...
                </p>
              </div>
            </div>
          )}

          {message && (
            <div className={`
              absolute bottom-4 left-1/2 transform -translate-x-1/2
              px-4 py-2 rounded-lg text-sm font-semibold
              transition-all duration-300 animate-slide-up
              ${message.includes("failed") 
                ? "bg-red-500/20 text-red-400 border border-red-500/30" 
                : "bg-green-500/20 text-green-400 border border-green-500/30"
              }
            `}>
              {message}
            </div>
          )}
        </div>

        {/* Overall Progress Bar */}
        {documentsArray.length > 0 && (
          <div className="bg-neutral-900/50 border border-neutral-800 rounded-xl p-6 space-y-4 backdrop-blur-sm">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold text-white">
                Processing {documentsArray.length} document{documentsArray.length !== 1 ? 's' : ''}
              </h3>
              <span className="text-sm text-gray-400">
                {Math.round(totalProgress / PIPELINE_STEPS.length * 100)}% Complete
              </span>
            </div>
            <div className="w-full bg-neutral-800 rounded-full h-2 overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-blue-500 to-purple-500 rounded-full transition-all duration-500 ease-out"
                style={{ width: `${(totalProgress / PIPELINE_STEPS.length) * 100}%` }}
              />
            </div>
          </div>
        )}

        {/* Pipeline Progress for Each Document */}
        {documentsArray.length > 0 && (
          <div className="space-y-4">
            {documentsArray.map(([docId, docInfo], index) => {
              const status = docInfo.progress_step ?? 0;
              const isReady = docInfo.ready ?? false;
              const currentStage = docInfo.status || "QUEUED";
              const progressPercent = ((status + 1) / PIPELINE_STEPS.length) * 100;

              return (
                <div
                  key={docId}
                  className={`
                    bg-neutral-900/50 border rounded-xl p-6 space-y-4
                    backdrop-blur-sm transition-all duration-300
                    ${isReady 
                      ? 'border-green-500/50 bg-green-500/5' 
                      : 'border-neutral-800 hover:border-neutral-700'
                    }
                    animate-slide-in
                  `}
                  style={{ animationDelay: `${index * 100}ms` }}
                >
                  {/* Document Header */}
                  <div className="flex justify-between items-start">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-3 mb-2">
                        <div className={`
                          w-2 h-2 rounded-full transition-all duration-300
                          ${isReady ? 'bg-green-400 animate-pulse' : 'bg-blue-400'}
                        `} />
                        <h4 className="text-white font-semibold truncate">
                          {docInfo.filename || docId}
                        </h4>
                      </div>
                      <div className="text-xs text-gray-400 space-x-3">
                        <span>ID: {docId}</span>
                        <span>•</span>
                        <span>v{docInfo.version}</span>
                        <span>•</span>
                        <span className="text-blue-400">{currentStage}</span>
                      </div>
                    </div>
                    {isReady && (
                      <div className="flex items-center gap-2 px-3 py-1 bg-green-500/20 border border-green-500/30 rounded-full">
                        <svg className="w-4 h-4 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                        <span className="text-green-400 text-sm font-semibold">Ready</span>
                      </div>
                    )}
                  </div>

                  {/* Progress Bar */}
                  <div className="space-y-2">
                    <div className="w-full bg-neutral-800 rounded-full h-1.5 overflow-hidden">
                      <div
                        className={`
                          h-full rounded-full transition-all duration-500 ease-out
                          ${isReady 
                            ? 'bg-gradient-to-r from-green-500 to-emerald-500' 
                            : 'bg-gradient-to-r from-blue-500 to-purple-500'
                          }
                        `}
                        style={{ width: `${progressPercent}%` }}
                      />
                    </div>
                    <div className="flex justify-between items-center text-xs">
                      <span className="text-gray-400">
                        Step {Math.max(0, status)} of {PIPELINE_STEPS.length - 1}
                      </span>
                      <span className="text-gray-500">
                        {PIPELINE_STEPS[Math.max(0, Math.min(status, PIPELINE_STEPS.length - 1))]}
                      </span>
                    </div>
                  </div>

                  {/* Multi-Step Progress Indicator */}
                  <div className="relative">
                    <div className="flex justify-between items-center">
                      {PIPELINE_STEPS.map((step, idx) => (
                        <div key={step} className="flex-1 flex flex-col items-center">
                          <div className="relative w-full flex items-center">
                            {/* Connection Line */}
                            {idx < PIPELINE_STEPS.length - 1 && (
                              <div className={`
                                absolute left-1/2 w-full h-0.5 -z-10
                                transition-all duration-500
                                ${idx < status 
                                  ? 'bg-gradient-to-r from-blue-500 to-purple-500' 
                                  : 'bg-neutral-700'
                                }
                              `} />
                            )}
                            
                            {/* Step Circle */}
                            <div className={`
                              relative w-8 h-8 rounded-full flex items-center justify-center
                              transition-all duration-500
                              ${idx <= status
                                ? isReady && idx === PIPELINE_STEPS.length - 1
                                  ? 'bg-green-500 scale-110 shadow-lg shadow-green-500/50'
                                  : 'bg-gradient-to-br from-blue-500 to-purple-500 scale-110 shadow-lg shadow-blue-500/50'
                                : 'bg-neutral-700 scale-100'
                              }
                            `}>
                              {idx < status || (isReady && idx === PIPELINE_STEPS.length - 1) ? (
                                <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                </svg>
                              ) : idx === status ? (
                                <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
                              ) : (
                                <div className="w-2 h-2 bg-neutral-400 rounded-full" />
                              )}
                            </div>
                          </div>
                          
                          {/* Step Label */}
                          <p className={`
                            mt-2 text-xs text-center max-w-[80px] transition-colors duration-300
                            ${idx <= status 
                              ? 'text-white font-medium' 
                              : 'text-gray-500'
                            }
                          `}>
                            {step}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              );
            })}

            {/* All Ready Banner */}
            {allReady && documentsArray.length > 0 && (
              <div className="bg-gradient-to-r from-green-500/20 to-emerald-500/20 border border-green-500/50 rounded-xl p-6 text-center backdrop-blur-sm animate-fade-in">
                <div className="flex items-center justify-center gap-3 mb-2">
                  <svg className="w-6 h-6 text-green-400 animate-bounce" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                  <p className="text-green-400 font-bold text-lg">
                    All documents ready!
                  </p>
                </div>
                <p className="text-green-300 text-sm">
                  Redirecting to chat in 2 seconds...
                </p>
              </div>
            )}
          </div>
        )}
      </section>

      <style jsx>{`
        @keyframes fade-in {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes slide-up {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes slide-in {
          from {
            opacity: 0;
            transform: translateX(-20px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }

        .animate-fade-in {
          animation: fade-in 0.5s ease-out;
        }

        .animate-slide-up {
          animation: slide-up 0.3s ease-out;
        }

        .animate-slide-in {
          animation: slide-in 0.4s ease-out both;
        }
      `}</style>
    </main>
  );
}
