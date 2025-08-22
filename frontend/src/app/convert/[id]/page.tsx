    /**
     * Conversion status page
     */

    "use client";

    import { useParams, useRouter } from "next/navigation";
    import { ConversionStatusDisplay } from "@/components/ConversionStatus";
    import { ArrowLeft } from "lucide-react";

    export default function ConvertPage() {
    const params = useParams();
    const router = useRouter();
    const jobId = params.id as string;

    const handleComplete = (audioUrl: string) => {
        // Could redirect to player page or show success message
        console.log("Conversion completed:", audioUrl);
    };

    return (
        <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
            <div className="max-w-2xl mx-auto">
            <button
                onClick={() => router.push("/")}
                className="flex items-center text-gray-600 hover:text-gray-900 mb-6"
            >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to upload
            </button>

            <div className="bg-white rounded-lg shadow-sm p-6">
                <h1 className="text-2xl font-bold text-gray-900 mb-6">
                Converting your document
                </h1>
                
                <ConversionStatusDisplay
                jobId={jobId}
                onComplete={handleComplete}
                />
            </div>
            </div>
        </div>
        </div>
    );
}