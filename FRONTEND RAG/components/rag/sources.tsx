"use client";

import { ChevronDown, FileText } from "lucide-react";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import type { Source } from "@/lib/api";
import { useState } from "react";

interface SourcesDisplayProps {
  sources: Source[];
}

export function SourcesDisplay({ sources }: SourcesDisplayProps) {
  const [isOpen, setIsOpen] = useState(false);

  if (sources.length === 0) return null;

  return (
    <Collapsible open={isOpen} onOpenChange={setIsOpen} className="mt-3">
      <CollapsibleTrigger className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors">
        <FileText className="size-4" />
        <span>{sources.length} source{sources.length > 1 ? "s" : ""}</span>
        <ChevronDown
          className={`size-4 transition-transform ${isOpen ? "rotate-180" : ""}`}
        />
      </CollapsibleTrigger>
      <CollapsibleContent className="mt-2 space-y-2">
        {sources.map((source, index) => (
          <div
            key={index}
            className="bg-muted/50 rounded-lg p-3 text-sm border border-border/50"
          >
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-medium bg-primary/10 text-primary px-2 py-0.5 rounded">
                Page {source.page ?? "N/A"}
              </span>
            </div>
            <p className="text-muted-foreground line-clamp-3">{source.content || "No source snippet available."}</p>
          </div>
        ))}
      </CollapsibleContent>
    </Collapsible>
  );
}
