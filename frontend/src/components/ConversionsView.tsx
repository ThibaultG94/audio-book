'use client';
import React, { useState } from 'react';
import { FileAudio, Play, Download, ChevronRight } from 'lucide-react';
import ChaptersList from './ChaptersList';
import ConversionProgress from './ConversionProgress';

interface Book {
    book_id: string;
    book_title: string;
    total_chapters: number;
    chapters: any[];
    estimated_duration_seconds: number;
  }
  
  interface ConversionJob {
    status: string;
    progress: number;
    chaptersCompleted: number;
    currentChapter?: string;
  }
  
  interface ConversionsViewProps {
    books: Book[];
    conversionJobs: Record<string, ConversionJob>;
    setConversionJobs: React.Dispatch<React.SetStateAction<Record<string, ConversionJob>>>;
    selectedBook: Book | null;
    setSelectedBook: React.Dispatch<React.SetStateAction<Book | null>>;
  }

  export default function ConversionsView({ books, conversionJobs, setConversionJobs, selectedBook, setSelectedBook }: ConversionsViewProps) {
    const [activeTab, setActiveTab] = useState('chapters');
  
    const startConversion = async (bookId: string) => {
        // Simulate starting conversion
        const newJob: ConversionJob = {
          status: 'processing',
          progress: 0,
          chaptersCompleted: 0,
          currentChapter: 'Chapter 1'
        };
        
        setConversionJobs({
          ...conversionJobs,
          [bookId]: newJob
        });
    
        // Simulate progress updates
        let progress = 0;
        const interval = setInterval(() => {
          progress += 0.1;
          if (progress >= 1) {
            clearInterval(interval);
            setConversionJobs((prev: Record<string, ConversionJob>) => ({
              ...prev,
              [bookId]: {
                ...prev[bookId],
                status: 'completed',
                progress: 1,
                chaptersCompleted: selectedBook?.total_chapters || 0
              }
            }));
          } else {
            setConversionJobs((prev: Record<string, ConversionJob>) => ({
              ...prev,
              [bookId]: {
                ...prev[bookId],
                progress,
                chaptersCompleted: Math.floor(progress * (selectedBook?.total_chapters || 0)),
                currentChapter: `Chapter ${Math.floor(progress * (selectedBook?.total_chapters || 0)) + 1}`
              }
            }));
          }
        }, 1000);
      };    
  
    if (books.length === 0) {
      return (
        <div className="text-center py-12">
          <FileAudio className="w-16 h-16 mx-auto mb-4 text-gray-300" />
          <h3 className="text-xl font-medium text-gray-600 mb-2">No Books Yet</h3>
          <p className="text-gray-500">Upload a book to get started with conversion</p>
        </div>
      );
    }
  
    return (
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Books List */}
        <div className="lg:col-span-1">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Your Books</h3>
          <div className="space-y-2">
            {books.map((book) => (
              <div
                key={book.book_id}
                onClick={() => setSelectedBook(book)}
                className={`p-4 rounded-lg border cursor-pointer transition-all ${
                  selectedBook?.book_id === book.book_id
                    ? 'border-indigo-500 bg-indigo-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-800">{book.book_title}</h4>
                    <p className="text-sm text-gray-500 mt-1">
                      {book.total_chapters} chapters
                    </p>
                  </div>
                  <ChevronRight className="w-5 h-5 text-gray-400 mt-1" />
                </div>
                
                {conversionJobs[book.book_id] && (
                  <div className="mt-3">
                    <ConversionProgress job={conversionJobs[book.book_id]} />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
  
        {/* Book Details */}
        {selectedBook && (
          <div className="lg:col-span-2">
            <div className="mb-6">
              <h3 className="text-2xl font-bold text-gray-800">{selectedBook.book_title}</h3>
              <p className="text-gray-600 mt-1">
                {selectedBook.total_chapters} chapters • 
                Est. {Math.floor(selectedBook.estimated_duration_seconds / 3600)}h {Math.floor((selectedBook.estimated_duration_seconds % 3600) / 60)}m
              </p>
            </div>
  
            {/* Action Buttons */}
            <div className="flex gap-4 mb-6">
              {!conversionJobs[selectedBook.book_id] ? (
                <button
                  onClick={() => startConversion(selectedBook.book_id)}
                  className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors flex items-center"
                >
                  <Play className="w-4 h-4 mr-2" />
                  Start Conversion
                </button>
              ) : conversionJobs[selectedBook.book_id].status === 'completed' ? (
                <button className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center">
                  <Download className="w-4 h-4 mr-2" />
                  Download All
                </button>
              ) : null}
            </div>
  
            {/* Tabs */}
            <div className="border-b border-gray-200 mb-6">
              <div className="flex space-x-8">
                <button
                  onClick={() => setActiveTab('chapters')}
                  className={`pb-2 px-1 border-b-2 font-medium text-sm transition-colors ${
                    activeTab === 'chapters'
                      ? 'border-indigo-500 text-indigo-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Chapters
                </button>
                <button
                  onClick={() => setActiveTab('settings')}
                  className={`pb-2 px-1 border-b-2 font-medium text-sm transition-colors ${
                    activeTab === 'settings'
                      ? 'border-indigo-500 text-indigo-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Settings
                </button>
              </div>
            </div>
  
            {/* Tab Content */}
            {activeTab === 'chapters' && (
              <ChaptersList 
                chapters={selectedBook.chapters}
                conversionJob={conversionJobs[selectedBook.book_id]}
              />
            )}
            
            {activeTab === 'settings' && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Voice Model
                  </label>
                  <select className="w-full px-4 py-2 border border-gray-300 rounded-lg">
                    <option>Amy (Medium Quality)</option>
                    <option>John (High Quality)</option>
                    <option>Sarah (Premium)</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Speech Speed
                  </label>
                  <input 
                    type="range"
                    min="0.5"
                    max="2"
                    step="0.1"
                    defaultValue="1"
                    className="w-full"
                  />
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    );
  }