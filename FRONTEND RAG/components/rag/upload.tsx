"use client";

import { useCallback, useState } from "react";
import { Upload, FileText, CheckCircle2, XCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";
import { uploadFiles, processFiles } from "@/lib/api";

const ALLOWED_FILE_RE = /\.(pdf|txt|docx|csv|xlsx|xls)$/i;

function isAllowedDocumentFile(file: File): boolean {
  return ALLOWED_FILE_RE.test(file.name);
}

interface FileUploadProps {
  onProcessComplete: () => void;
}

export function FileUpload({ onProcessComplete }: FileUploadProps) {
  const [files, setFiles] = useState<File[]>([]);
  const [uploadedPaths, setUploadedPaths] = useState<string[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<"idle" | "uploading" | "success" | "error">("idle");
  const [processStatus, setProcessStatus] = useState<"idle" | "processing" | "success" | "error">("idle");
  const [errorMessage, setErrorMessage] = useState("");

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const droppedFiles = Array.from(e.dataTransfer.files).filter(isAllowedDocumentFile);
    
    if (droppedFiles.length > 0) {
      setFiles((prev) => [...prev, ...droppedFiles]);
      setUploadStatus("idle");
      setProcessStatus("idle");
    }
  }, []);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files).filter(isAllowedDocumentFile);
      setFiles((prev) => [...prev, ...selectedFiles]);
      setUploadStatus("idle");
      setProcessStatus("idle");
    }
  }, []);

  const handleUpload = async () => {
    if (files.length === 0) return;

    setUploadStatus("uploading");
    setErrorMessage("");

    try {
      const response = await uploadFiles(files);
      setUploadedPaths(response.paths);
      setUploadStatus("success");
    } catch (error) {
      setUploadStatus("error");
      setErrorMessage(error instanceof Error ? error.message : "Failed to upload files. Please try again.");
    }
  };

  const handleProcess = async () => {
    if (uploadedPaths.length === 0) return;

    setProcessStatus("processing");
    setErrorMessage("");

    try {
      await processFiles(uploadedPaths);
      setProcessStatus("success");
      localStorage.setItem("rag-ready", "true");
      onProcessComplete();
    } catch (error) {
      setProcessStatus("error");
      setErrorMessage(error instanceof Error ? error.message : "Failed to process files. Please try again.");
    }
  };

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
    localStorage.removeItem("rag-ready");
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="size-5" />
          Upload documents
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
            isDragging
              ? "border-primary bg-primary/5"
              : "border-muted-foreground/25 hover:border-primary/50"
          }`}
        >
          <Upload className="size-10 mx-auto text-muted-foreground mb-4" />
          <p className="text-muted-foreground mb-2">
            Drag and drop PDF, TXT, Word, CSV, or Excel files here, or
          </p>
          <label>
            <input
              type="file"
              multiple
              accept=".pdf,.txt,.docx,.csv,.xlsx,.xls,application/pdf,text/plain,text/csv"
              onChange={handleFileSelect}
              className="hidden"
            />
            <span className="text-primary cursor-pointer hover:underline">
              browse files
            </span>
          </label>
        </div>

        {files.length > 0 && (
          <div className="space-y-2">
            <p className="text-sm font-medium">Selected files:</p>
            <ul className="space-y-1">
              {files.map((file, index) => (
                <li
                  key={index}
                  className="flex items-center justify-between text-sm bg-muted p-2 rounded"
                >
                  <span className="truncate">{file.name}</span>
                  <button
                    onClick={() => removeFile(index)}
                    className="text-muted-foreground hover:text-destructive ml-2"
                  >
                    <XCircle className="size-4" />
                  </button>
                </li>
              ))}
            </ul>
          </div>
        )}

        {errorMessage && (
          <p className="text-sm text-destructive">{errorMessage}</p>
        )}

        <div className="flex gap-2">
          <Button
            onClick={handleUpload}
            disabled={files.length === 0 || uploadStatus === "uploading"}
            className="flex-1"
          >
            {uploadStatus === "uploading" ? (
              <>
                <Spinner className="mr-2" />
                Uploading...
              </>
            ) : uploadStatus === "success" ? (
              <>
                <CheckCircle2 className="size-4 mr-2" />
                Uploaded
              </>
            ) : (
              "Upload Files"
            )}
          </Button>

          <Button
            onClick={handleProcess}
            disabled={uploadStatus !== "success" || processStatus === "processing"}
            variant={processStatus === "success" ? "outline" : "default"}
            className="flex-1"
          >
            {processStatus === "processing" ? (
              <>
                <Spinner className="mr-2" />
                Processing...
              </>
            ) : processStatus === "success" ? (
              <>
                <CheckCircle2 className="size-4 mr-2" />
                Processed
              </>
            ) : (
              "Process Files"
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
