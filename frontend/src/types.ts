export interface ResumeData {
  name: string;
  email: string;
  phone: string;
  summary: string;
  skills: string[];
  experience: ExperienceEntry[];
  education: EducationEntry[];
  certifications: string[];
  raw_text?: string;
}

export interface ExperienceEntry {
  title?: string;
  title_line?: string;
  company?: string;
  company_line?: string;
  dates?: string;
  bullets?: string[] | string;
}

export interface EducationEntry {
  degree?: string;
  degree_line?: string;
  institution?: string;
  dates?: string;
  details?: string;
}

export interface MatchResult {
  match_score: number;
  keyword_score: number;
  ai_score: number;
  missing_skills: string[];
  matched_skills: string[];
  weak_areas: string[];
  suggestions: string[];
  keyword_overlap: string[];
  missing_keywords: string[];
}

export interface ChangeSummary {
  section: string;
  type: string;
  description: string;
}

export interface AnalyzeResponse {
  original_resume: ResumeData;
  match_result: MatchResult;
  optimized_resume: ResumeData;
  optimized_match_score: number;
  changes_summary: ChangeSummary[];
}
