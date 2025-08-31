'use client';
import React, { useState, useCallback } from 'react';
import { Upload, FileAudio, Loader2, CheckCircle } from 'lucide-react';

interface UploadResult {
  book_id: string;
  book_title: string;
  total_chapters: number;
  chapters: any[];
  estimated_duration_seconds: number;
}

interface UploadFormProps {
  onUploadSuccess: (book: UploadResult) => void;
}

export default function UploadForm({ onUploadSuccess }: UploadFormProps) {
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState('');
  const [author, setAuthor] = useState('');
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [uploadResult, setUploadResult] = useState<UploadResult | null>(null);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  }, []);

  const handleFile = (selectedFile: File) => {
    const ext = selectedFile.name.split('.').pop()?.toLowerCase();
    if (!ext || !['pdf', 'epub'].includes(ext)) {
      alert('Please select a PDF or EPUB file');
      return;
    }
    setFile(selectedFile);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    if (title) formData.append('title', title);
    if (author) formData.append('author', author);

    try {
      // Simulated API call - replace with actual endpoint
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const result: UploadResult = {
        book_id: `book_${Date.now()}`,
        book_title: title || file.name.replace(/\.[^/.]+$/, ""),
        total_chapters: Math.floor(Math.random() * 10) + 5,
        chapters: [],
        estimated_duration_seconds: Math.floor(Math.random() * 7200) + 3600
      };

      // Generate mock chapters
      for (let i = 0; i < result.total_chapters; i++) {
        result.chapters.push({
          index: i,
          title: `Chapter ${i + 1}`,
          status: 'pending',
          estimated_duration_seconds: Math.floor(Math.random() * 1800) + 600
        });
      }

      setUploadResult(result);
      onUploadSuccess(result);
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Upload Your Book</h2>
        
        {/* Drop Zone */}
        <div
          className={`relative border-2 border-dashed rounded-lg p-12 text-center transition-all ${
            dragActive 
              ? 'border-indigo-500 bg-indigo-50' 
              : 'border-gray-300 hover:border-gray-400'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <input
            type="file"
            accept=".pdf,.epub"
            onChange={handleFileChange}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          />
          
          <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
          
          {file ? (
            <div>
              <p className="text-lg font-medium text-gray-800">{file.name}</p>
              <p className="text-sm text-gray-500 mt-1">
                {(file.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
          ) : (
            <div>
              <p className="text-lg text-gray-600">
                Drop your PDF or EPUB file here, or click to browse
              </p>
              <p className="text-sm text-gray-400 mt-2">
                Maximum file size: 500MB
              </p>
            </div>
          )}
        </div>

        {/* Optional Metadata */}
        {file && (
          <div className="mt-6 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Book Title (optional)
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Enter book title"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Author (optional)
              </label>
              <input
                type="text"
                value={author}
                onChange={(e) => setAuthor(e.target.value)}
                placeholder="Enter author name"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>
          </div>
        )}

        {/* Upload Button */}
        {file && (
          <button
            onClick={handleUpload}
            disabled={uploading}
            className="mt-6 w-full bg-indigo-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
          >
            {uploading ? (
              <>
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                Processing Book...
              </>
            ) : (
              <>
                <FileAudio className="w-5 h-5 mr-2" />
                Start Conversion
              </>
            )}
          </button>
        )}
      </div>

      {/* Upload Result */}
      {uploadResult && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-6">
          <div className="flex items-start">
            <CheckCircle className="w-6 h-6 text-green-500 mt-1 mr-3 flex-shrink-0" />
            <div className="flex-1">
              <h3 className="font-medium text-green-900">Book Analyzed Successfully!</h3>
              <p className="text-green-700 mt-1">
                Found {uploadResult.total_chapters} chapters • 
                Estimated duration: {Math.floor(uploadResult.estimated_duration_seconds / 3600)}h {Math.floor((uploadResult.estimated_duration_seconds % 3600) / 60)}m
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}