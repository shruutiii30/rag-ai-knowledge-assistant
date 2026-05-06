"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { Send, MessageSquare } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { MessageBubble, TypingIndicator, type Message } from "./message";
import { askQuestion } from "@/lib/api";

interface ChatInterfaceProps {
  isReady: boolean;
}

export function ChatInterface({ isReady }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = useCallback(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading, scrollToBottom]);

  useEffect(() => {
    const savedMessages = localStorage.getItem("chat-history");
    if (savedMessages) {
      try {
        setMessages(JSON.parse(savedMessages));
      } catch {
        // Invalid JSON, ignore
      }
    }
  }, []);

  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem("chat-history", JSON.stringify(messages));
    }
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!input.trim() || isLoading || !isReady) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input.trim(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);
    setErrorMessage("");

    try {
      const response = await askQuestion(userMessage.content);
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: response.answer,
        sources: Array.isArray(response.sources) ? response.sources : [],
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Failed to get answer.";
      setErrorMessage(message);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: `Sorry, I couldn't process that request.\n\n${message}`,
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const clearHistory = () => {
    setMessages([]);
    localStorage.removeItem("chat-history");
  };

  return (
    <Card className="flex flex-col h-[600px]">
      <CardHeader className="flex-shrink-0 border-b">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <MessageSquare className="size-5" />
            Chat with your PDFs
          </CardTitle>
          {messages.length > 0 && (
            <Button variant="ghost" size="sm" onClick={clearHistory}>
              Clear
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col p-0 overflow-hidden">
        <ScrollArea className="flex-1 p-4">
          <div ref={scrollRef} className="space-y-4">
            {messages.length === 0 ? (
              <div className="h-full flex items-center justify-center text-center text-muted-foreground py-20">
                <div>
                  <MessageSquare className="size-12 mx-auto mb-4 opacity-50" />
                  <p className="text-lg font-medium">No messages yet</p>
                  <p className="text-sm">
                    {isReady
                      ? "Ask a question about your uploaded documents"
                      : "Upload and process PDFs to start chatting"}
                  </p>
                </div>
              </div>
            ) : (
              <>
                {messages.map((message) => (
                  <MessageBubble key={message.id} message={message} />
                ))}
                {isLoading && <TypingIndicator />}
              </>
            )}
          </div>
        </ScrollArea>

        <form
          onSubmit={handleSubmit}
          className="flex-shrink-0 border-t p-4 bg-background"
        >
          {errorMessage && (
            <p className="mb-2 text-sm text-destructive">{errorMessage}</p>
          )}
          <div className="flex gap-2">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={
                isReady
                  ? "Ask a question about your documents..."
                  : "Upload and process PDFs first..."
              }
              disabled={!isReady || isLoading}
              className="flex-1 px-4 py-2 rounded-lg border bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring disabled:opacity-50 disabled:cursor-not-allowed"
            />
            <Button
              type="submit"
              disabled={!input.trim() || isLoading || !isReady}
              size="icon"
            >
              <Send className="size-4" />
              <span className="sr-only">Send message</span>
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
