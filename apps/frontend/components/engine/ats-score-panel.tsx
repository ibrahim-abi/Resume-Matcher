'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { calculateAtsScore, ATSScore, EngineFlowResult } from '@/lib/api/engine';
import { Loader2, Activity, CheckCircle, AlertTriangle, ArrowRight } from 'lucide-react';

interface AtsScorePanelProps {
  resumeId: string;
  initialScoreData?: Record<string, unknown>;
}

export function AtsScorePanel({ resumeId, initialScoreData }: AtsScorePanelProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [jobDescription, setJobDescription] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<EngineFlowResult | null>(null);

  useEffect(() => {
    if (initialScoreData) {
      setResult({
        resume_id: resumeId,
        ats_score: initialScoreData.ats_score as ATSScore,
        job_requirements:
          initialScoreData.job_requirements as unknown as EngineFlowResult['job_requirements'],
        optimized_resume: {} as Record<string, unknown>, // Dummy since we don't display the resume here
      });
      setIsOpen(true);
    }
  }, [initialScoreData, resumeId]);

  const handleCalculate = async () => {
    if (!jobDescription.trim()) {
      setError('Please paste a job description first.');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const res = await calculateAtsScore(resumeId, jobDescription);
      setResult(res);
      setIsOpen(true);
    } catch (err) {
      console.error('Failed to calculate ATS score:', err);
      setError('Failed to calculate ATS score. Make sure LLM is configured.');
    } finally {
      setIsLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-700 bg-green-50';
    if (score >= 60) return 'text-amber-700 bg-amber-50';
    return 'text-red-700 bg-red-50';
  };

  return (
    <Card className="w-full flex-shrink-0 relative overflow-hidden bg-white shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] border-2 border-black">
      <div
        className="p-4 border-b-2 border-black bg-blue-700 text-white flex justify-between items-center cursor-pointer"
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="flex items-center gap-2">
          <Activity className="w-5 h-5" />
          <h3 className="font-mono font-bold uppercase tracking-widest text-sm">
            Engine Flow ATS Score
          </h3>
        </div>
        <span className="font-mono text-xs">{isOpen ? '▼' : '►'}</span>
      </div>

      {isOpen && (
        <div className="p-4 space-y-4">
          {!result ? (
            <div className="space-y-3">
              <p className="font-mono text-xs text-gray-600 uppercase">
                Paste Job Description to Analyze
              </p>
              <textarea
                className="w-full h-32 p-3 font-mono text-sm border-2 border-black focus:outline-none focus:ring-0 resize-none"
                placeholder="Paste the job description here..."
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
              />
              {error && <p className="font-mono text-xs text-red-600 uppercase">{error}</p>}
              <Button
                className="w-full justify-center"
                onClick={handleCalculate}
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" /> ANALYZING...
                  </>
                ) : (
                  <>
                    <Activity className="w-4 h-4 mr-2" /> CALCULATE SCORE
                  </>
                )}
              </Button>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Overall Score */}
              <div
                className={`p-4 border-2 border-black text-center ${getScoreColor(result.ats_score.score_percentage)}`}
              >
                <p className="font-mono text-xs font-bold uppercase tracking-widest mb-1">
                  Overall Match
                </p>
                <p className="font-serif text-5xl font-black">
                  {result.ats_score.score_percentage}%
                </p>
              </div>

              {/* Dimension Scores */}
              <div className="space-y-3">
                <ScoreDimension
                  label="Semantic Keyword Match"
                  score={result.ats_score.semantic_keyword_match}
                  weight="40%"
                />
                <ScoreDimension
                  label="Impact & Metrics"
                  score={result.ats_score.impact_and_metrics}
                  weight="30%"
                />
                <ScoreDimension
                  label="Action Language"
                  score={result.ats_score.action_oriented_language}
                  weight="20%"
                />
                <ScoreDimension
                  label="Clarity & Brevity"
                  score={result.ats_score.clarity_and_brevity}
                  weight="10%"
                />
              </div>

              {/* Extracted Details */}
              <div className="border-t-2 border-black pt-4 space-y-4">
                <div>
                  <h4 className="font-mono text-xs font-bold uppercase tracking-widest mb-2 flex items-center gap-1 text-green-700">
                    <CheckCircle className="w-3 h-3" /> Matched Keywords
                  </h4>
                  <div className="flex flex-wrap gap-1">
                    {result.ats_score.matched_keywords.length > 0 ? (
                      result.ats_score.matched_keywords.map((kw, i) => (
                        <span
                          key={i}
                          className="px-2 py-0.5 border border-black text-[10px] font-mono uppercase bg-green-50"
                        >
                          {kw}
                        </span>
                      ))
                    ) : (
                      <span className="text-xs font-mono text-gray-500">None found</span>
                    )}
                  </div>
                </div>

                <div>
                  <h4 className="font-mono text-xs font-bold uppercase tracking-widest mb-2 flex items-center gap-1 text-red-700">
                    <AlertTriangle className="w-3 h-3" /> Missing Keywords
                  </h4>
                  <div className="flex flex-wrap gap-1">
                    {result.ats_score.missing_keywords.length > 0 ? (
                      result.ats_score.missing_keywords.map((kw, i) => (
                        <span
                          key={i}
                          className="px-2 py-0.5 border border-black text-[10px] font-mono uppercase bg-red-50"
                        >
                          {kw}
                        </span>
                      ))
                    ) : (
                      <span className="text-xs font-mono text-gray-500">None missing</span>
                    )}
                  </div>
                </div>

                <div>
                  <h4 className="font-mono text-xs font-bold uppercase tracking-widest mb-2">
                    Recommendations
                  </h4>
                  <ul className="space-y-2">
                    {result.ats_score.recommendations.map((rec, i) => (
                      <li key={i} className="flex gap-2 text-sm">
                        <ArrowRight className="w-4 h-4 flex-shrink-0 text-blue-700 mt-0.5" />
                        <span>{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              <div className="pt-2">
                <Button
                  variant="outline"
                  className="w-full text-xs"
                  onClick={() => setResult(null)}
                >
                  Analyze Another Job
                </Button>
              </div>
            </div>
          )}
        </div>
      )}
    </Card>
  );
}

function ScoreDimension({
  label,
  score,
  weight,
}: {
  label: string;
  score: number;
  weight: string;
}) {
  const getProgressBarColor = (s: number) => {
    if (s >= 80) return 'bg-green-600';
    if (s >= 60) return 'bg-amber-500';
    return 'bg-red-600';
  };

  return (
    <div>
      <div className="flex justify-between items-end mb-1">
        <span className="font-mono text-[10px] uppercase font-bold text-gray-700">
          {label}{' '}
          <span className="text-gray-400 font-normal ml-1 w-8 inline-block">({weight})</span>
        </span>
        <span className="font-mono text-[10px] font-bold">{score}%</span>
      </div>
      <div className="h-2 w-full border border-black bg-gray-100 overflow-hidden">
        <div
          className={`h-full border-r border-black ${getProgressBarColor(score)}`}
          style={{ width: `${score}%` }}
        />
      </div>
    </div>
  );
}
