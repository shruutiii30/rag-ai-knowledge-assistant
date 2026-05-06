const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000";

export interface UploadResponse {
  message: string;
  paths: string[];
}

export interface ProcessResponse {
  message: string;
  total_chunks: number;
}

export interface Source {
  page?: number | null;
  content: string;
}

export interface AskResponse {
  question: string;
  answer: string;
  sources: Source[];
}

async function parseApiError(response: Response, fallback: string): Promise<Error> {
  try {
    const data = await response.json();
    if (typeof data?.error === "string" && data.error.trim()) {
      return new Error(data.error);
    }
    if (typeof data?.message === "string" && data.message.trim()) {
      return new Error(data.message);
    }
  } catch {
    // Ignore JSON parsing failures and use fallback message.
  }

  return new Error(fallback);
}

export async function uploadFiles(files: File[]): Promise<UploadResponse> {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append("files", file);
  });

  const response = await fetch(`${API_BASE_URL}/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw await parseApiError(response, "Upload failed");
  }

  return response.json();
}

export async function processFiles(filePaths: string[]): Promise<ProcessResponse> {
  const response = await fetch(`${API_BASE_URL}/process`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ file_paths: filePaths }),
  });

  if (!response.ok) {
    throw await parseApiError(response, "Processing failed");
  }

  return response.json();
}

export async function askQuestion(query: string): Promise<AskResponse> {
  const response = await fetch(`${API_BASE_URL}/ask`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ query }),
  });

  if (!response.ok) {
    throw await parseApiError(response, "Query failed");
  }

  return response.json();
}
