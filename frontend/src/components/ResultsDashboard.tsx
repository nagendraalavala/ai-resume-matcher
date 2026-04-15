import { useState } from "react";
import {
  ArrowLeft,
  Download,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Lightbulb,
  BarChart3,
  FileText,
  ArrowUpRight,
  Sparkles,
} from "lucide-react";
import {
  RadialBarChart,
  RadialBar,
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
} from "recharts";
import axios from "axios";
import type { AnalyzeResponse } from "../types";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

interface ResultsDashboardProps {
  data: AnalyzeResponse;
  onBack: () => void;
}

export default function ResultsDashboard({
  data,
  onBack,
}: ResultsDashboardProps) {
  const [activeTab, setActiveTab] = useState<
    "overview" | "comparison" | "optimized"
  >("overview");
  const [isDownloading, setIsDownloading] = useState(false);

  const { match_result, optimized_resume, optimized_match_score, changes_summary } =
    data;

  const scoreColor =
    match_result.match_score >= 70
      ? "#22c55e"
      : match_result.match_score >= 50
      ? "#f59e0b"
      : "#ef4444";

  const optimizedColor =
    optimized_match_score >= 70
      ? "#22c55e"
      : optimized_match_score >= 50
      ? "#f59e0b"
      : "#ef4444";

  const handleDownload = async () => {
    setIsDownloading(true);
    try {
      const formData = new FormData();
      formData.append("resume_data", JSON.stringify(optimized_resume));

      const response = await axios.post(`${API_URL}/api/download-pdf`, formData, {
        responseType: "blob",
        timeout: 30000,
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", "optimized_resume.pdf");
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch {
      alert("Failed to download PDF. Please try again.");
    } finally {
      setIsDownloading(false);
    }
  };

  const radialData = [
    {
      name: "Original",
      value: match_result.match_score,
      fill: scoreColor,
    },
  ];

  const pieData = [
    { name: "Keyword", value: match_result.keyword_score },
    { name: "AI Semantic", value: match_result.ai_score },
  ];

  const PIE_COLORS = ["#3b82f6", "#8b5cf6"];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={onBack}
              className="p-2 rounded-lg hover:bg-slate-100 text-slate-600 transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div className="flex items-center gap-2">
              <div className="bg-blue-600 text-white p-2 rounded-xl">
                <Sparkles className="w-5 h-5" />
              </div>
              <h1 className="text-lg font-bold text-slate-900">
                Analysis Results
              </h1>
            </div>
          </div>
          <button
            onClick={handleDownload}
            disabled={isDownloading}
            className="flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-medium rounded-xl transition-all shadow-md"
          >
            <Download className="w-4 h-4" />
            {isDownloading ? "Generating..." : "Download Optimized PDF"}
          </button>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-6">
        {/* Score Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          {/* Current Score */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6 text-center">
            <p className="text-sm text-slate-500 mb-2">Current Match</p>
            <div className="w-32 h-32 mx-auto">
              <ResponsiveContainer width="100%" height="100%">
                <RadialBarChart
                  innerRadius="70%"
                  outerRadius="100%"
                  data={radialData}
                  startAngle={90}
                  endAngle={-270}
                >
                  <RadialBar
                    dataKey="value"
                    cornerRadius={10}
                    background={{ fill: "#f1f5f9" }}
                  />
                </RadialBarChart>
              </ResponsiveContainer>
            </div>
            <p
              className="text-3xl font-bold -mt-20 mb-16"
              style={{ color: scoreColor }}
            >
              {match_result.match_score}%
            </p>
          </div>

          {/* Optimized Score */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6 text-center relative overflow-hidden">
            <div className="absolute top-3 right-3 bg-green-100 text-green-700 text-xs font-medium px-2 py-1 rounded-full flex items-center gap-1">
              <ArrowUpRight className="w-3 h-3" />+
              {optimized_match_score - match_result.match_score}%
            </div>
            <p className="text-sm text-slate-500 mb-2">After Optimization</p>
            <div className="w-32 h-32 mx-auto">
              <ResponsiveContainer width="100%" height="100%">
                <RadialBarChart
                  innerRadius="70%"
                  outerRadius="100%"
                  data={[
                    {
                      name: "Optimized",
                      value: optimized_match_score,
                      fill: optimizedColor,
                    },
                  ]}
                  startAngle={90}
                  endAngle={-270}
                >
                  <RadialBar
                    dataKey="value"
                    cornerRadius={10}
                    background={{ fill: "#f1f5f9" }}
                  />
                </RadialBarChart>
              </ResponsiveContainer>
            </div>
            <p
              className="text-3xl font-bold -mt-20 mb-16"
              style={{ color: optimizedColor }}
            >
              {optimized_match_score}%
            </p>
          </div>

          {/* Score Breakdown */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6">
            <p className="text-sm text-slate-500 mb-2 text-center">
              Score Breakdown
            </p>
            <div className="w-32 h-32 mx-auto">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    innerRadius={35}
                    outerRadius={55}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {pieData.map((_entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={PIE_COLORS[index % PIE_COLORS.length]}
                      />
                    ))}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="flex justify-center gap-4 mt-2">
              <div className="flex items-center gap-1.5">
                <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                <span className="text-xs text-slate-600">
                  Keyword {match_result.keyword_score}%
                </span>
              </div>
              <div className="flex items-center gap-1.5">
                <div className="w-3 h-3 rounded-full bg-violet-500"></div>
                <span className="text-xs text-slate-600">
                  Semantic {match_result.ai_score}%
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-1 bg-white rounded-xl border border-slate-200 p-1 mb-6">
          {(
            [
              { key: "overview", label: "Overview", icon: BarChart3 },
              { key: "comparison", label: "Changes Made", icon: FileText },
              { key: "optimized", label: "Optimized Resume", icon: Sparkles },
            ] as const
          ).map(({ key, label, icon: Icon }) => (
            <button
              key={key}
              onClick={() => setActiveTab(key)}
              className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-medium transition-all ${
                activeTab === key
                  ? "bg-blue-600 text-white shadow-sm"
                  : "text-slate-600 hover:bg-slate-50"
              }`}
            >
              <Icon className="w-4 h-4" />
              {label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        {activeTab === "overview" && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Matched Skills */}
            <div className="bg-white rounded-2xl border border-slate-200 p-6">
              <div className="flex items-center gap-2 mb-4">
                <CheckCircle2 className="w-5 h-5 text-green-600" />
                <h3 className="font-semibold text-slate-900">
                  Matched Skills ({match_result.matched_skills.length})
                </h3>
              </div>
              <div className="flex flex-wrap gap-2">
                {match_result.matched_skills.length > 0 ? (
                  match_result.matched_skills.map((skill, i) => (
                    <span
                      key={i}
                      className="px-3 py-1 bg-green-50 text-green-700 text-sm rounded-full border border-green-200"
                    >
                      {skill}
                    </span>
                  ))
                ) : (
                  <p className="text-sm text-slate-400">
                    No matched skills identified
                  </p>
                )}
              </div>
            </div>

            {/* Missing Skills */}
            <div className="bg-white rounded-2xl border border-slate-200 p-6">
              <div className="flex items-center gap-2 mb-4">
                <XCircle className="w-5 h-5 text-red-500" />
                <h3 className="font-semibold text-slate-900">
                  Missing Skills ({match_result.missing_skills.length})
                </h3>
              </div>
              <div className="flex flex-wrap gap-2">
                {match_result.missing_skills.length > 0 ? (
                  match_result.missing_skills.map((skill, i) => (
                    <span
                      key={i}
                      className="px-3 py-1 bg-red-50 text-red-700 text-sm rounded-full border border-red-200"
                    >
                      {skill}
                    </span>
                  ))
                ) : (
                  <p className="text-sm text-slate-400">
                    Great! No major skill gaps found.
                  </p>
                )}
              </div>
            </div>

            {/* Weak Areas */}
            <div className="bg-white rounded-2xl border border-slate-200 p-6">
              <div className="flex items-center gap-2 mb-4">
                <AlertTriangle className="w-5 h-5 text-amber-500" />
                <h3 className="font-semibold text-slate-900">Weak Areas</h3>
              </div>
              <ul className="space-y-2">
                {match_result.weak_areas.length > 0 ? (
                  match_result.weak_areas.map((area, i) => (
                    <li
                      key={i}
                      className="flex items-start gap-2 text-sm text-slate-700"
                    >
                      <span className="text-amber-500 mt-0.5">&#9679;</span>
                      {area}
                    </li>
                  ))
                ) : (
                  <p className="text-sm text-slate-400">
                    No significant weak areas found.
                  </p>
                )}
              </ul>
            </div>

            {/* Suggestions */}
            <div className="bg-white rounded-2xl border border-slate-200 p-6">
              <div className="flex items-center gap-2 mb-4">
                <Lightbulb className="w-5 h-5 text-blue-500" />
                <h3 className="font-semibold text-slate-900">
                  AI Suggestions
                </h3>
              </div>
              <ul className="space-y-2">
                {match_result.suggestions.length > 0 ? (
                  match_result.suggestions.map((suggestion, i) => (
                    <li
                      key={i}
                      className="flex items-start gap-2 text-sm text-slate-700"
                    >
                      <span className="text-blue-500 mt-0.5">&#10148;</span>
                      {suggestion}
                    </li>
                  ))
                ) : (
                  <p className="text-sm text-slate-400">
                    Your resume looks well-aligned!
                  </p>
                )}
              </ul>
            </div>
          </div>
        )}

        {activeTab === "comparison" && (
          <div className="bg-white rounded-2xl border border-slate-200 p-6">
            <h3 className="font-semibold text-slate-900 mb-4">
              Changes Summary
            </h3>
            <div className="space-y-4">
              {changes_summary.map((change, i) => (
                <div
                  key={i}
                  className="flex items-start gap-4 p-4 bg-slate-50 rounded-xl"
                >
                  <div
                    className={`shrink-0 px-3 py-1 rounded-full text-xs font-medium ${
                      change.type === "modified"
                        ? "bg-blue-100 text-blue-700"
                        : change.type === "enhanced"
                        ? "bg-purple-100 text-purple-700"
                        : change.type === "improved"
                        ? "bg-green-100 text-green-700"
                        : "bg-slate-200 text-slate-600"
                    }`}
                  >
                    {change.type}
                  </div>
                  <div>
                    <p className="font-medium text-slate-900">
                      {change.section}
                    </p>
                    <p className="text-sm text-slate-600 mt-1">
                      {change.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === "optimized" && (
          <div className="bg-white rounded-2xl border border-slate-200 p-8">
            <div className="max-w-2xl mx-auto">
              {/* Name */}
              {optimized_resume.name && (
                <h2 className="text-2xl font-bold text-slate-900 text-center mb-1">
                  {optimized_resume.name}
                </h2>
              )}

              {/* Contact */}
              <div className="text-center text-sm text-slate-500 mb-6">
                {[optimized_resume.email, optimized_resume.phone]
                  .filter(Boolean)
                  .join(" | ")}
              </div>

              {/* Summary */}
              {optimized_resume.summary && (
                <div className="mb-6">
                  <h3 className="text-sm font-bold text-blue-700 uppercase tracking-wide border-b border-slate-200 pb-1 mb-3">
                    Professional Summary
                  </h3>
                  <p className="text-sm text-slate-700 leading-relaxed">
                    {optimized_resume.summary}
                  </p>
                </div>
              )}

              {/* Skills */}
              {optimized_resume.skills &&
                optimized_resume.skills.length > 0 && (
                  <div className="mb-6">
                    <h3 className="text-sm font-bold text-blue-700 uppercase tracking-wide border-b border-slate-200 pb-1 mb-3">
                      Skills
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {optimized_resume.skills.map((skill, i) => (
                        <span
                          key={i}
                          className="px-2 py-0.5 bg-slate-100 text-slate-700 text-sm rounded"
                        >
                          {typeof skill === "string" ? skill : String(skill)}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

              {/* Experience */}
              {optimized_resume.experience &&
                optimized_resume.experience.length > 0 && (
                  <div className="mb-6">
                    <h3 className="text-sm font-bold text-blue-700 uppercase tracking-wide border-b border-slate-200 pb-1 mb-3">
                      Experience
                    </h3>
                    {optimized_resume.experience.map((exp, i) => (
                      <div key={i} className="mb-4">
                        <p className="font-semibold text-slate-900 text-sm">
                          {exp.title || exp.title_line}
                        </p>
                        {(exp.company || exp.company_line) && (
                          <p className="text-sm text-slate-500 italic">
                            {exp.company || exp.company_line}
                            {exp.dates ? ` | ${exp.dates}` : ""}
                          </p>
                        )}
                        {exp.bullets && (
                          <ul className="mt-1 space-y-1">
                            {(Array.isArray(exp.bullets)
                              ? exp.bullets
                              : String(exp.bullets).split("\n")
                            )
                              .filter(Boolean)
                              .map((bullet, j) => (
                                <li
                                  key={j}
                                  className="text-sm text-slate-700 flex items-start gap-2"
                                >
                                  <span className="text-slate-400 mt-1">
                                    &#8226;
                                  </span>
                                  {bullet}
                                </li>
                              ))}
                          </ul>
                        )}
                      </div>
                    ))}
                  </div>
                )}

              {/* Education */}
              {optimized_resume.education &&
                optimized_resume.education.length > 0 && (
                  <div className="mb-6">
                    <h3 className="text-sm font-bold text-blue-700 uppercase tracking-wide border-b border-slate-200 pb-1 mb-3">
                      Education
                    </h3>
                    {optimized_resume.education.map((edu, i) => (
                      <div key={i} className="mb-2">
                        <p className="font-semibold text-slate-900 text-sm">
                          {edu.degree || edu.degree_line}
                        </p>
                        {edu.institution && (
                          <p className="text-sm text-slate-500 italic">
                            {edu.institution}
                            {edu.dates ? ` | ${edu.dates}` : ""}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                )}

              {/* Certifications */}
              {optimized_resume.certifications &&
                optimized_resume.certifications.length > 0 && (
                  <div className="mb-6">
                    <h3 className="text-sm font-bold text-blue-700 uppercase tracking-wide border-b border-slate-200 pb-1 mb-3">
                      Certifications
                    </h3>
                    <ul className="space-y-1">
                      {optimized_resume.certifications.map((cert, i) => (
                        <li key={i} className="text-sm text-slate-700">
                          {cert}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
            </div>
          </div>
        )}

        {/* Download CTA */}
        <div className="mt-8 text-center">
          <button
            onClick={handleDownload}
            disabled={isDownloading}
            className="inline-flex items-center gap-2 px-8 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-semibold rounded-xl transition-all shadow-lg shadow-blue-600/25"
          >
            <Download className="w-5 h-5" />
            {isDownloading
              ? "Generating PDF..."
              : "Download Optimized Resume (PDF)"}
          </button>
        </div>
      </main>
    </div>
  );
}
