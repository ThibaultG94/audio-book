'use client';
import React from 'react';
import { CheckCircle, Loader2, Play, Download } from 'lucide-react';

interface Chapter {
    index: number;
    title: string;
    estimated_duration_seconds: number;
  }
  
  interface ConversionJob {
    status: string;
    chaptersCompleted: number;
  }
  
  interface ChaptersListProps {
    chapters: Chapter[];
    conversionJob?: ConversionJob;
  }

  export default function ChaptersList({ chapters, conversionJob }: ChaptersListProps) {
    const getChapterStatus = (index: number) => {
      if (!conversionJob) return 'pending';
      if (conversionJob.status === 'completed') return 'completed';
      if (conversionJob.chaptersCompleted > index) return 'completed';
      if (conversionJob.chaptersCompleted === index) return 'processing';
      return 'pending';
    };
  
    return (
      <div className="space-y-2">
        {chapters.map((chapter) => {
          const status = getChapterStatus(chapter.index);
          
          return (
            <div
              key={chapter.index}
              className="flex items-center justify-between p-4 rounded-lg border border-gray-200 hover:border-gray-300 transition-colors"
            >
              <div className="flex items-center flex-1">
                <div className="mr-4">
                  {status === 'completed' ? (
                    <CheckCircle className="w-5 h-5 text-green-500" />
                  ) : status === 'processing' ? (
                    <Loader2 className="w-5 h-5 text-indigo-600 animate-spin" />
                  ) : (
                    <div className="w-5 h-5 rounded-full border-2 border-gray-300" />
                  )}
                </div>
                
                <div className="flex-1">
                  <h4 className="font-medium text-gray-800">{chapter.title}</h4>
                  <p className="text-sm text-gray-500">
                    ~{Math.floor(chapter.estimated_duration_seconds / 60)} minutes
                  </p>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                {status === 'completed' && (
                  <>
                    <button className="p-2 text-gray-600 hover:text-indigo-600 transition-colors">
                      <Play className="w-4 h-4" />
                    </button>
                    <button className="p-2 text-gray-600 hover:text-indigo-600 transition-colors">
                      <Download className="w-4 h-4" />
                    </button>
                  </>
                )}
              </div>
            </div>
          );
        })}
      </div>
    );
  }
  