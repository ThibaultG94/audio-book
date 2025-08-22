/**
 * Home page with file upload
 */

"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { FileUpload } from "@/components/FileUpload";
import { api } from "@/lib/api";
import { FileUploadResponse, ConversionRequest } from "@/lib/types";

export default function HomePage() {
  const [isUploading, setIsUploading] = useState(false);
  const [isConverting, setIsConverting] = useState(false);
  const router = useRouter();

  const handleFileUploaded = async (uploadResponse: FileUploadResponse) => {
    setIsConverting(true);

    try {
      const conversionRequest: ConversionRequest = {
        file_id: uploadResponse.file_id,
        // Use default TTS settings
      };

      const conversionResponse = await api.startConversion(conversionRequest);

      // Redirect to conversion status page
      router.push(`/convert/${conversionResponse.job_id}`);
    } catch (error) {
      console.error("Failed to start conversion:", error);
      setIsConverting(false);
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Audio Book Converter
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Convert your PDF and EPUB documents to high-quality audio books 
          using AI-powered text-to-speech technology.
          </p>
        </div>

        <div className="max-w-lg mx-auto">
          <FileUpload onFileUploaded={handleFileUploaded} isLoading={isUploading || isConverting}/> 

          {isConverting && (
            <div className="mt-6 text-center">
              <p className="text-gray-600">Starting conversion...</p>
            </div>
          )}
        </div>

      <div className="mt-16 text-center">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">
            How it works
          </h2>
          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-blue-600 font-bold text-lg">1</span>
              </div>
              <h3 className="font-semibold mb-2">Upload Document</h3>
              <p className="text-gray-600">Upload your PDF or EPUB file</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-blue-600 font-bold text-lg">2</span>
              </div>
              <h3 className="font-semibold mb-2">AI Processing</h3>
              <p className="text-gray-600">Our AI converts text to natural speech</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-blue-600 font-bold text-lg">3</span>
              </div>
              <h3 className="font-semibold mb-2">Download Audio</h3>
              <p className="text-gray-600">Get your high-quality audio book</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
