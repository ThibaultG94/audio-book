'use client';
import React from 'react';

interface ConversionJob {
    status: string;
    currentChapter?: string;
    progress: number;
  }
  
  interface ConversionProgressProps {
    job?: ConversionJob;
  }

  export default function ConversionProgress({ job }: ConversionProgressProps) {
    if (!job) return null;
  
    return (
      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">
            {job.status === 'completed' ? 'Completed' : job.currentChapter}
          </span>
          <span className="text-gray-600">
            {Math.round(job.progress * 100)}%
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all duration-500 ${
              job.status === 'completed' ? 'bg-green-500' : 'bg-indigo-600'
            }`}
            style={{ width: `${job.progress * 100}%` }}
          />
        </div>
      </div>
    );
  }