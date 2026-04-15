import { useState, useRef, useCallback } from "react";
import {
  Upload,
  FileText,
  Link,
  SlidersHorizontal,
  Sparkles,
  X,
  AlertCircle,
} from "lucide-react";
import axios from "axios";
import type { AnalyzeResponse } from "../types";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

interface UploadPageProps {
  onResults: (data: AnalyzeResponse) => void;
}

export default function UploadPage({ onResults }: UploadPageProps) {
  const [file, setFile] = useState<File | null>(null);
  const [inputMode, setInputMode] = useState<"text" | "url">("text");
  const [jobDescription, setJobDescription] = useState("");
  const [jobUrl, setJobUrl] = useState("");
  const [targetPercentage, setTargetPercentage] = useState(85);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState("");
  const [error, setError] = useState("");
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      const ext = droppedFile.name.split(".").pop()?.toLowerCase();
      if (ext === "pdf" || ext === "docx") {
        setFile(droppedFile);
        setError("");
      } else {
        setError("Please upload a PDF or DOCX file.");
      }
    }
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      const ext = selectedFile.name.split(".").pop()?.toLowerCase();
      if (ext === "pdf" || ext === "docx") {
        setFile(selectedFile);
        setError("");
      } else {
        setError("Please upload a PDF or DOCX file.");
      }
    }
  };

  const handleSubmit = async () => {
    setError("");

    if (!file) {
      setError("Please upload your resume.");
      return;
    }

    if (inputMode === "text" && !jobDescription.trim()) {
      setError("Please enter a job description.");
      return;
    }

    if (inputMode === "url" && !jobUrl.trim()) {
      setError("Please enter a job URL.");
      return;
    }

    setIsLoading(true);

    try {
      const formData = new FormData();
      formData.append("resume", file);
      formData.append("target_percentage", targetPercentage.toString());

      if (inputMode === "text") {
        formData.append("job_description", jobDescription);
      } else {
        formData.append("job_url", jobUrl);
      }

      setLoadingStep("Parsing your resume...");
      await new Promise((r) => setTimeout(r, 500));

      setLoadingStep("Analyzing match with job description...");

      const response = await axios.post<AnalyzeResponse>(
        `${API_URL}/api/analyze`,
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
          timeout: 120000,
        }
      );

      setLoadingStep("Preparing results...");
      await new Promise((r) => setTimeout(r, 300));

      onResults(response.data);
    } catch (err) {
      if (axios.isAxiosError(err)) {
        const detail = err.response?.data?.detail;
        setError(
          typeof detail === "string"
            ? detail
            : "An error occurred while analyzing your resume. Please try again."
        );
      } else {
        setError("An unexpected error occurred. Please try again.");
      }
    } finally {
      setIsLoading(false);
      setLoadingStep("");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-4 py-4 flex items-center gap-3">
          <div className="bg-blue-600 text-white p-2 rounded-xl">
            <Sparkles className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-900">
              AI Resume Matcher
            </h1>
            <p className="text-sm text-slate-500">
              Match, optimize & download your resume
            </p>
          </div>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-4 py-8">
        {/* Loading Overlay */}
        {isLoading && (
          <div className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 flex items-center justify-center">
            <div className="bg-white rounded-2xl p-8 max-w-sm w-full mx-4 text-center shadow-2xl">
              <div className="relative mx-auto w-16 h-16 mb-4">
                <div className="absolute inset-0 rounded-full border-4 border-blue-100"></div>
                <div className="absolute inset-0 rounded-full border-4 border-blue-600 border-t-transparent animate-spin"></div>
                <Sparkles className="absolute inset-0 m-auto w-6 h-6 text-blue-600" />
              </div>
              <h3 className="text-lg font-semibold text-slate-900 mb-1">
                AI is working...
              </h3>
              <p className="text-sm text-slate-500">{loadingStep}</p>
              <div className="mt-4 bg-slate-100 rounded-full h-1.5 overflow-hidden">
                <div className="h-full bg-blue-600 rounded-full animate-pulse w-2/3"></div>
              </div>
            </div>
          </div>
        )}

        {/* Step 1: Upload Resume */}
        <section className="mb-8">
          <div className="flex items-center gap-2 mb-3">
            <span className="flex items-center justify-center w-7 h-7 rounded-full bg-blue-600 text-white text-sm font-bold">
              1
            </span>
            <h2 className="text-lg font-semibold text-slate-900">
              Upload Your Resume
            </h2>
          </div>

          <div
            className={`relative border-2 border-dashed rounded-xl p-8 text-center transition-all cursor-pointer ${
              dragOver
                ? "border-blue-500 bg-blue-50"
                : file
                ? "border-green-400 bg-green-50"
                : "border-slate-300 bg-white hover:border-blue-400 hover:bg-blue-50/50"
            }`}
            onDragOver={(e) => {
              e.preventDefault();
              setDragOver(true);
            }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleFileDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.docx"
              className="hidden"
              onChange={handleFileSelect}
            />

            {file ? (
              <div className="flex items-center justify-center gap-3">
                <FileText className="w-8 h-8 text-green-600" />
                <div className="text-left">
                  <p className="font-medium text-slate-900">{file.name}</p>
                  <p className="text-sm text-slate-500">
                    {(file.size / 1024).toFixed(1)} KB
                  </p>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setFile(null);
                  }}
                  className="ml-2 p-1 rounded-full hover:bg-red-100 text-slate-400 hover:text-red-600 transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            ) : (
              <>
                <Upload className="w-10 h-10 text-slate-400 mx-auto mb-3" />
                <p className="text-slate-700 font-medium">
                  Drop your resume here or click to browse
                </p>
                <p className="text-sm text-slate-400 mt-1">
                  PDF or DOCX format
                </p>
              </>
            )}
          </div>
        </section>

        {/* Step 2: Job Description */}
        <section className="mb-8">
          <div className="flex items-center gap-2 mb-3">
            <span className="flex items-center justify-center w-7 h-7 rounded-full bg-blue-600 text-white text-sm font-bold">
              2
            </span>
            <h2 className="text-lg font-semibold text-slate-900">
              Job Description
            </h2>
          </div>

          <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
            {/* Tabs */}
            <div className="flex border-b border-slate-200">
              <button
                className={`flex-1 px-4 py-3 text-sm font-medium flex items-center justify-center gap-2 transition-colors ${
                  inputMode === "text"
                    ? "text-blue-600 border-b-2 border-blue-600 bg-blue-50/50"
                    : "text-slate-500 hover:text-slate-700"
                }`}
                onClick={() => setInputMode("text")}
              >
                <FileText className="w-4 h-4" />
                Paste Text
              </button>
              <button
                className={`flex-1 px-4 py-3 text-sm font-medium flex items-center justify-center gap-2 transition-colors ${
                  inputMode === "url"
                    ? "text-blue-600 border-b-2 border-blue-600 bg-blue-50/50"
                    : "text-slate-500 hover:text-slate-700"
                }`}
                onClick={() => setInputMode("url")}
              >
                <Link className="w-4 h-4" />
                Job URL
              </button>
            </div>

            <div className="p-4">
              {inputMode === "text" ? (
                <textarea
                  className="w-full h-48 px-4 py-3 rounded-lg border border-slate-200 focus:border-blue-400 focus:ring-2 focus:ring-blue-100 outline-none resize-none text-sm text-slate-700 placeholder-slate-400"
                  placeholder="Paste the full job description here..."
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                />
              ) : (
                <div>
                  <input
                    type="url"
                    className="w-full px-4 py-3 rounded-lg border border-slate-200 focus:border-blue-400 focus:ring-2 focus:ring-blue-100 outline-none text-sm text-slate-700 placeholder-slate-400"
                    placeholder="https://www.linkedin.com/jobs/view/..."
                    value={jobUrl}
                    onChange={(e) => setJobUrl(e.target.value)}
                  />
                  <p className="text-xs text-slate-400 mt-2">
                    Supports LinkedIn, Indeed, Dice, Glassdoor, and most job
                    posting URLs
                  </p>
                </div>
              )}
            </div>
          </div>
        </section>

        {/* Step 3: Target Percentage */}
        <section className="mb-8">
          <div className="flex items-center gap-2 mb-3">
            <span className="flex items-center justify-center w-7 h-7 rounded-full bg-blue-600 text-white text-sm font-bold">
              3
            </span>
            <h2 className="text-lg font-semibold text-slate-900">
              Target Match Score
            </h2>
          </div>

          <div className="bg-white rounded-xl border border-slate-200 p-5">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2 text-slate-600">
                <SlidersHorizontal className="w-4 h-4" />
                <span className="text-sm">Target percentage</span>
              </div>
              <span className="text-2xl font-bold text-blue-600">
                {targetPercentage}%
              </span>
            </div>
            <input
              type="range"
              min="70"
              max="95"
              step="5"
              value={targetPercentage}
              onChange={(e) => setTargetPercentage(parseInt(e.target.value))}
              className="w-full h-2 bg-slate-200 rounded-full appearance-none cursor-pointer accent-blue-600"
            />
            <div className="flex justify-between text-xs text-slate-400 mt-1">
              <span>70%</span>
              <span>95%</span>
            </div>
          </div>
        </section>

        {/* Error */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-xl p-4 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}

        {/* Submit Button */}
        <button
          onClick={handleSubmit}
          disabled={isLoading}
          className="w-full py-4 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-semibold rounded-xl transition-all flex items-center justify-center gap-2 text-lg shadow-lg shadow-blue-600/25 hover:shadow-blue-600/40"
        >
          <Sparkles className="w-5 h-5" />
          {isLoading ? "Analyzing..." : "Analyze & Optimize Resume"}
        </button>

        <p className="text-center text-xs text-slate-400 mt-3">
          Your resume is processed securely and not stored permanently.
        </p>
      </main>
    </div>
  );
}
