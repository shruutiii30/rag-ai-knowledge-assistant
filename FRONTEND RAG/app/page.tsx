"use client";

import { useEffect, useState } from "react";
import { FileUpload } from "@/components/rag/upload";
import { ChatInterface } from "@/components/rag/chat";
import { FileText } from "lucide-react";

export default function Home() {
  const [isProcessed, setIsProcessed] = useState(false);

  useEffect(() => {
    const ready = localStorage.getItem("rag-ready");
    setIsProcessed(ready === "true");
  }, []);

  return (
    <main className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8 max-w-5xl">
        <header className="text-center mb-8">
          <div className="inline-flex items-center justify-center size-16 rounded-2xl bg-primary/10 mb-4">
            <FileText className="size-8 text-primary" />
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-balance">
            PDF Question Answering
          </h1>
          <p className="text-muted-foreground mt-2 text-balance">
            Upload your PDF documents and ask questions about their content
          </p>
        </header>

        <div className="grid gap-6 lg:grid-cols-[380px_1fr]">
          <div className="space-y-6">
            <FileUpload onProcessComplete={() => setIsProcessed(true)} />
            
            <div className="bg-muted/50 rounded-lg p-4 text-sm">
              <h3 className="font-medium mb-2">How it works</h3>
              <ol className="list-decimal list-inside space-y-1 text-muted-foreground">
                <li>Upload one or more PDF files</li>
                <li>Click &quot;Process Files&quot; to index content</li>
                <li>Ask questions about your documents</li>
              </ol>
            </div>
          </div>

          <ChatInterface isReady={isProcessed} />
        </div>
      </div>
    </main>
  );
}
