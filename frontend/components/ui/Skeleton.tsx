import React from "react";

export function Skeleton({ className }: { className?: string }) {
  return (
    <div className={`animate-pulse bg-gray-200 rounded ${className}`} />
  );
}

export function TaskSkeleton() {
  return (
    <div className="flex items-center justify-between p-4 border rounded shadow-sm mb-2 bg-white opacity-60">
      <div className="flex items-center gap-3 w-full">
        <Skeleton className="w-5 h-5 rounded-full" />
        <div className="flex-1 space-y-2">
          <Skeleton className="h-4 w-3/4" />
          <Skeleton className="h-3 w-1/2" />
        </div>
      </div>
    </div>
  );
}
