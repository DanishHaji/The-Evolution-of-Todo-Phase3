"use client";

import React, { useState } from "react";
import { api } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Trash2, Loader2, Sparkles, Edit, Check, X, Calendar, Clock } from "lucide-react";
import { toast } from "sonner";
import { motion } from "framer-motion";
import { Input } from "@/components/ui/input";

interface Task {
  id: string;
  title: string;
  description?: string;
  status: boolean;
  due_date?: string;
  priority?: string;
}

export function TaskItem({ task, onRefresh }: { task: Task; onRefresh: () => void }) {
  const [loading, setLoading] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(task.title);
  const [editDescription, setEditDescription] = useState(task.description || "");

  const toggleComplete = async () => {
    setLoading(true);
    try {
      await api.patch(`/api/tasks/${task.id}`, { status: !task.status });
      toast.success(
        task.status ? "Task marked as incomplete" : "Task completed! 🎉",
        {
          icon: task.status ? "↩️" : "✅",
        }
      );
      onRefresh();
    } catch (error: any) {
      toast.error(error.message || "Failed to update task");
    } finally {
      setLoading(false);
    }
  };

  const deleteTask = async () => {
    setIsDeleting(true);
    try {
      await api.delete(`/api/tasks/${task.id}`);
      toast.success("Task deleted successfully", { icon: "🗑️" });
      setTimeout(() => {
        onRefresh();
      }, 300);
    } catch (error: any) {
      toast.error(error.message || "Failed to delete task");
      setIsDeleting(false);
    }
  };

  const saveEdit = async () => {
    if (!editTitle.trim()) {
      toast.error("Task title cannot be empty");
      return;
    }

    setLoading(true);
    try {
      await api.patch(`/api/tasks/${task.id}`, {
        title: editTitle,
        description: editDescription
      });
      toast.success("Task updated successfully", { icon: "✏️" });
      setIsEditing(false);
      onRefresh();
    } catch (error: any) {
      toast.error(error.message || "Failed to update task");
    } finally {
      setLoading(false);
    }
  };

  const cancelEdit = () => {
    setEditTitle(task.title);
    setEditDescription(task.description || "");
    setIsEditing(false);
  };

  return (
    <motion.div
      layout
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{
        opacity: isDeleting ? 0 : 1,
        scale: isDeleting ? 0.95 : 1,
        x: isDeleting ? -20 : 0
      }}
      exit={{ opacity: 0, scale: 0.95, x: -20 }}
      transition={{ duration: 0.2 }}
    >
      <Card className="group p-5 hover:shadow-xl transition-all duration-300 bg-white/80 dark:bg-gray-900/80 backdrop-blur-lg border-2 border-gray-200 dark:border-gray-800 hover:border-blue-300 dark:hover:border-blue-700">
        {isEditing ? (
          <div className="space-y-3">
            <Input
              value={editTitle}
              onChange={(e) => setEditTitle(e.target.value)}
              placeholder="Task title"
              className="font-semibold"
              disabled={loading}
            />
            <Input
              value={editDescription}
              onChange={(e) => setEditDescription(e.target.value)}
              placeholder="Description (optional)"
              className="text-sm"
              disabled={loading}
            />
            <div className="flex gap-2 justify-end">
              <Button
                size="sm"
                variant="outline"
                onClick={cancelEdit}
                disabled={loading}
              >
                <X className="h-4 w-4 mr-1" />
                Cancel
              </Button>
              <Button
                size="sm"
                onClick={saveEdit}
                disabled={loading}
                className="bg-gradient-to-r from-blue-600 to-purple-600 text-white"
              >
                {loading ? (
                  <Loader2 className="h-4 w-4 mr-1 animate-spin" />
                ) : (
                  <Check className="h-4 w-4 mr-1" />
                )}
                Save
              </Button>
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-4 flex-1">
              <motion.div
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
              >
                <Checkbox
                  checked={task.status}
                  onCheckedChange={toggleComplete}
                  disabled={loading}
                  className="w-6 h-6 border-2 data-[state=checked]:bg-gradient-to-r data-[state=checked]:from-blue-600 data-[state=checked]:to-purple-600 data-[state=checked]:border-0"
                />
              </motion.div>
              <div className="flex-1">
                <h3
                  className={`font-semibold text-base transition-all duration-300 ${
                    task.status
                      ? "line-through text-gray-400 dark:text-gray-600"
                      : "text-gray-900 dark:text-white"
                  }`}
                >
                  {task.title}
                  {task.status && (
                    <motion.span
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      className="ml-2 inline-block"
                    >
                      <Sparkles className="h-4 w-4 inline text-yellow-500" />
                    </motion.span>
                  )}
                </h3>
                {task.description && (
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                    {task.description}
                  </p>
                )}
                {task.due_date && (
                  <p className="text-xs text-blue-600 dark:text-blue-400 mt-1 flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {new Date(task.due_date).toLocaleString('en-US', {
                      month: 'short',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </p>
                )}
              </div>
            </div>
            <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
              <motion.div whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }}>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setIsEditing(true)}
                  disabled={loading || isDeleting}
                  className="text-blue-500 hover:text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-950/20"
                >
                  <Edit className="h-5 w-5" />
                </Button>
              </motion.div>
              <motion.div whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }}>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={deleteTask}
                  disabled={loading || isDeleting}
                  className="text-red-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-950/20"
                >
                  {loading || isDeleting ? (
                    <Loader2 className="h-5 w-5 animate-spin" />
                  ) : (
                    <Trash2 className="h-5 w-5" />
                  )}
                </Button>
              </motion.div>
            </div>
          </div>
        )}
      </Card>
    </motion.div>
  );
}
