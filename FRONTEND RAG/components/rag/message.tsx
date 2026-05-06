"use client";

import { User, Bot } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { SourcesDisplay } from "./sources";
import type { Source } from "@/lib/api";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
}

interface MessageBubbleProps {
  message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"}`}>
      {!isUser && (
        <div className="flex-shrink-0 size-8 rounded-full bg-primary/10 flex items-center justify-center">
          <Bot className="size-4 text-primary" />
        </div>
      )}
      <div
        className={`max-w-[80%] ${
          isUser
            ? "bg-primary text-primary-foreground rounded-2xl rounded-br-md px-4 py-2"
            : "bg-muted rounded-2xl rounded-bl-md px-4 py-3"
        }`}
      >
        {isUser ? (
          <p>{message.content}</p>
        ) : (
          <div className="prose prose-sm dark:prose-invert max-w-none">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {message.content}
            </ReactMarkdown>
          </div>
        )}
        {!isUser && message.sources && message.sources.length > 0 && (
          <SourcesDisplay sources={message.sources} />
        )}
      </div>
      {isUser && (
        <div className="flex-shrink-0 size-8 rounded-full bg-primary flex items-center justify-center">
          <User className="size-4 text-primary-foreground" />
        </div>
      )}
    </div>
  );
}

export function TypingIndicator() {
  return (
    <div className="flex gap-3 justify-start">
      <div className="flex-shrink-0 size-8 rounded-full bg-primary/10 flex items-center justify-center">
        <Bot className="size-4 text-primary" />
      </div>
      <div className="bg-muted rounded-2xl rounded-bl-md px-4 py-3">
        <div className="flex gap-1">
          <span className="size-2 bg-muted-foreground/50 rounded-full animate-bounce [animation-delay:0ms]" />
          <span className="size-2 bg-muted-foreground/50 rounded-full animate-bounce [animation-delay:150ms]" />
          <span className="size-2 bg-muted-foreground/50 rounded-full animate-bounce [animation-delay:300ms]" />
        </div>
      </div>
    </div>
  );
}
