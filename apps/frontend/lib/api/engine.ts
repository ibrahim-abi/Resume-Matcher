import { apiFetch } from './client';
import type { ResumeData } from '@/components/dashboard/resume-component';

export interface JobRequirements {
  required_skills: string[];
  preferred_skills: string[];
  technologies: string[];
  ats_keywords: string[];
  experience_level?: string;
  key_responsibilities: string[];
}

export interface ATSScore {
  score_percentage: number;
  semantic_keyword_match: number;
  impact_and_metrics: number;
  action_oriented_language: number;
  clarity_and_brevity: number;
  matched_keywords: string[];
  missing_keywords: string[];
  recommendations: string[];
}

export interface EngineFlowRequest {
  resume_id: string;
  job_description: string;
}

export interface EngineGenerateResponse {
  resume_id: string;
}

export interface EngineFlowResult {
  resume_id: string;
  job_requirements: JobRequirements;
  ats_score: ATSScore;
  optimized_resume: ResumeData;
  pdf_url?: string;
}

/**
 * Run the full engine flow (Analyze Job -> Optimize Resume -> Score ATS)
 */
export async function calculateAtsScore(
  resumeId: string,
  jobDescription: string
): Promise<EngineFlowResult> {
  const res = await apiFetch('/api/v1/engine/score', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      resume_id: resumeId,
      job_description: jobDescription,
    }),
  });

  if (!res.ok) {
    throw new Error(`Failed to calculate score: ${res.statusText}`);
  }

  return await res.json();
}

/**
 * Generate a new tailored resume natively via the Engine Flow and save directly.
 */
export async function generateEngineResume(
  resumeId: string,
  jobDescription: string
): Promise<EngineGenerateResponse> {
  const res = await apiFetch('/api/v1/engine/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      resume_id: resumeId,
      job_description: jobDescription,
    }),
  });

  if (!res.ok) {
    throw new Error(`Failed to generate engine resume: ${res.statusText}`);
  }

  return await res.json();
}

/**
 * Export the resume as a LaTeX compiled PDF
 */
export async function exportLatexPdf(resumeData: ResumeData): Promise<Blob> {
  const token = localStorage.getItem('token');
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  // Adjust port for backend if UI is on 3000
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const response = await fetch(`${apiUrl}/api/v1/engine/export-latex`, {
    method: 'POST',
    headers,
    body: JSON.stringify(resumeData),
  });

  if (!response.ok) {
    throw new Error('Failed to generate LaTeX PDF');
  }

  return await response.blob();
}
