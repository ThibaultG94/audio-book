'use client';
import React, { useState } from 'react';
import UploadForm from '@/components/UploadForm';
import ConversionsView from '@/components/ConversionsView';

interface Book {
  book_id: string;
  book_title: string;
  total_chapters: number;
  chapters: any[];
  estimated_duration_seconds: number;
}

export default function TTSConverterApp() {
  const [currentView, setCurrentView] = useState<'upload' | 'conversions'>('upload');
  const [books, setBooks] = useState<Book[]>([]);
  const [selectedBook, setSelectedBook] = useState<Book | null>(null);
  const [conversionJobs, setConversionJobs] = useState<Record<string, any>>({});

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            📚 Book to Audiobook Converter
          </h1>
          <p className="text-gray-600">
            Convert your PDF and EPUB books to high-quality audiobooks with AI voices
          </p>
        </header>

        {/* Navigation Tabs */}
        <div className="flex space-x-4 mb-8">
          <button
            onClick={() => setCurrentView('upload')}
            className={`px-6 py-3 rounded-lg font-medium transition-all ${
              currentView === 'upload'
                ? 'bg-white text-indigo-600 shadow-lg'
                : 'bg-white/50 text-gray-600 hover:bg-white/70'
            }`}
          >
            Upload Book
          </button>
          <button
            onClick={() => setCurrentView('conversions')}
            className={`px-6 py-3 rounded-lg font-medium transition-all ${
              currentView === 'conversions'
                ? 'bg-white text-indigo-600 shadow-lg'
                : 'bg-white/50 text-gray-600 hover:bg-white/70'
            }`}
          >
            My Conversions
          </button>
        </div>

        {/* Main Content */}
        <div className="bg-white rounded-2xl shadow-xl p-8">
          {currentView === 'upload' && (
            <UploadForm 
              onUploadSuccess={(book) => {
                setBooks([...books, book]);
                setCurrentView('conversions');
              }}
            />
          )}
          {currentView === 'conversions' && (
            <ConversionsView 
              books={books}
              conversionJobs={conversionJobs}
              setConversionJobs={setConversionJobs}
              selectedBook={selectedBook}
              setSelectedBook={setSelectedBook}
            />
          )}
        </div>
      </div>
    </div>
  );
}