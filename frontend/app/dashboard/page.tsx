"use client";

import React, { useEffect, useState, useMemo } from "react";
import { useAuth } from "@/context/AuthContext";
import { api } from "@/lib/api";
import { TaskItem } from "@/components/tasks/TaskItem";
import { EmptyState } from "@/components/tasks/EmptyState";
import { TaskSkeleton } from "@/components/ui/Skeleton";
import { toast } from "sonner";
import ProtectedRoute from "@/components/auth/ProtectedRoute";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { LogOut, Plus, Loader2, CheckCircle2, ListTodo, Target, TrendingUp, Clock, CheckCheck, Circle, MessageCircle } from "lucide-react";
import { motion } from "framer-motion";
import Link from "next/link";

type FilterType = "all" | "active" | "completed";

interface Task {
  id: string;
  title: string;
  description?: string;
  status: boolean;
  user_id: string;
  created_at: string;
  updated_at: string;
}

export default function Dashboard() {
  const { user, logout } = useAuth();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [dueDate, setDueDate] = useState("");
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [filter, setFilter] = useState<FilterType>("all");
  const [lastFetch, setLastFetch] = useState(0);

  const fetchTasks = async () => {
    try {
      const data = await api.get("/api/tasks") as Task[];
      console.log("Fetched tasks:", data.length, data); // Debug log
      setTasks(data);
      setLastFetch(Date.now()); // Track last fetch time
    } catch (error: any) {
      console.error("Fetch error:", error); // Debug log
      toast.error(error.message || "Failed to fetch tasks");
    }
  };

  useEffect(() => {
    const loadInitialTasks = async () => {
      setInitialLoading(true);
      await fetchTasks();
      setInitialLoading(false);
    };
    loadInitialTasks();
  }, []);

  // Auto-refresh every 2 seconds to keep UI in sync
  useEffect(() => {
    const interval = setInterval(() => {
      console.log("Auto-refresh triggered");
      fetchTasks();
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  const createTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    setLoading(true);
    try {
      const taskData: any = {
        title: title.trim(),
        description: description.trim() || undefined,
        due_date: dueDate || undefined
      };

      await api.post("/api/tasks/", taskData);
      setTitle("");
      setDescription("");
      setDueDate("");
      toast.success("Task created successfully! 🎉");
      await fetchTasks(); // Wait for fetch to complete
    } catch (error: any) {
      toast.error(error.message || "Failed to create task");
    } finally {
      setLoading(false);
    }
  };

  // Calculate statistics - Simple direct calculation
  const totalTasks = tasks.length;
  const completedTasks = tasks.filter(t => t.status === true).length;
  const activeTasks = tasks.filter(t => t.status === false).length;
  const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

  const stats = {
    total: totalTasks,
    completed: completedTasks,
    active: activeTasks,
    completionRate
  };

  // Filter tasks - Simple function, no useMemo
  const getFilteredTasks = () => {
    console.log(`=== FILTERING ===`);
    console.log(`Filter: ${filter}`);
    console.log(`Total tasks:`, tasks.length);
    console.log(`Tasks data:`, tasks);

    if (filter === "active") {
      const filtered = tasks.filter(task => task.status === false);
      console.log(`Active tasks:`, filtered.length, filtered);
      return filtered;
    }

    if (filter === "completed") {
      const filtered = tasks.filter(task => task.status === true);
      console.log(`Completed tasks:`, filtered.length, filtered);
      return filtered;
    }

    console.log(`All tasks:`, tasks.length);
    return tasks;
  };

  const filteredTasks = getFilteredTasks();

  const fadeIn = {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.4 }
  };

  const stagger = {
    animate: {
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50/30 to-purple-50/30 dark:from-gray-900 dark:via-gray-900 dark:to-gray-900">
        {/* Header */}
        <header className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-lg border-b border-gray-200 dark:border-gray-800 sticky top-0 z-10">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-purple-600">
                <CheckCircle2 className="h-5 w-5 text-white" />
              </div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent dark:from-blue-400 dark:to-purple-400">
                TaskFlow
              </h1>
            </div>
            <div className="flex items-center gap-4">
              <div className="hidden sm:block text-right">
                <p className="text-xs text-gray-500 dark:text-gray-400 font-medium uppercase tracking-wider">
                  Signed in as
                </p>
                <p className="text-sm font-medium text-gray-900 dark:text-white">{user?.email}</p>
              </div>
              <Link href="/dashboard/chat">
                <Button
                  size="sm"
                  className="gap-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-lg shadow-blue-500/25"
                >
                  <MessageCircle className="h-4 w-4" />
                  <span className="hidden sm:inline">AI Chat</span>
                </Button>
              </Link>
              <Button
                variant="outline"
                size="sm"
                onClick={logout}
                className="gap-2 hover:bg-red-50 hover:text-red-600 hover:border-red-200 dark:hover:bg-red-950 dark:hover:text-red-400 dark:hover:border-red-900"
              >
                <LogOut className="h-4 w-4" />
                <span className="hidden sm:inline">Logout</span>
              </Button>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Welcome Section */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="mb-8"
          >
            <h2 className="text-4xl font-bold tracking-tight mb-2 bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent dark:from-white dark:to-gray-300">
              Welcome back, {user?.email?.split('@')[0]}! 👋
            </h2>
            <p className="text-gray-600 dark:text-gray-400 text-lg">
              Here's your productivity overview for today
            </p>
          </motion.div>

          {/* Statistics Cards */}
          <motion.div
            variants={stagger}
            initial="initial"
            animate="animate"
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
          >
            <motion.div variants={fadeIn}>
              <Card className="bg-gradient-to-br from-blue-500 to-blue-600 border-0 shadow-lg shadow-blue-500/25 dark:shadow-blue-500/10">
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-blue-100 text-sm font-medium mb-1">Total Tasks</p>
                      <p className="text-4xl font-bold text-white">{stats.total}</p>
                    </div>
                    <div className="h-12 w-12 rounded-lg bg-white/20 flex items-center justify-center">
                      <ListTodo className="h-6 w-6 text-white" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            <motion.div variants={fadeIn}>
              <Card className="bg-gradient-to-br from-green-500 to-green-600 border-0 shadow-lg shadow-green-500/25 dark:shadow-green-500/10">
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-green-100 text-sm font-medium mb-1">Completed</p>
                      <p className="text-4xl font-bold text-white">{stats.completed}</p>
                    </div>
                    <div className="h-12 w-12 rounded-lg bg-white/20 flex items-center justify-center">
                      <CheckCheck className="h-6 w-6 text-white" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            <motion.div variants={fadeIn}>
              <Card className="bg-gradient-to-br from-orange-500 to-orange-600 border-0 shadow-lg shadow-orange-500/25 dark:shadow-orange-500/10">
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-orange-100 text-sm font-medium mb-1">Active Tasks</p>
                      <p className="text-4xl font-bold text-white">{stats.active}</p>
                    </div>
                    <div className="h-12 w-12 rounded-lg bg-white/20 flex items-center justify-center">
                      <Clock className="h-6 w-6 text-white" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            <motion.div variants={fadeIn}>
              <Card className="bg-gradient-to-br from-purple-500 to-purple-600 border-0 shadow-lg shadow-purple-500/25 dark:shadow-purple-500/10">
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-purple-100 text-sm font-medium mb-1">Completion</p>
                      <p className="text-4xl font-bold text-white">{stats.completionRate}%</p>
                    </div>
                    <div className="h-12 w-12 rounded-lg bg-white/20 flex items-center justify-center">
                      <TrendingUp className="h-6 w-6 text-white" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </motion.div>

          {/* Create Task Form */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <Card className="mb-8 border-2 border-gray-200 dark:border-gray-800 shadow-xl bg-white/80 dark:bg-gray-900/80 backdrop-blur-lg">
              <CardContent className="pt-6">
                <form onSubmit={createTask} className="space-y-4">
                  <div className="flex gap-3">
                    <Input
                      type="text"
                      placeholder="Task title (e.g., Buy groceries)"
                      value={title}
                      onChange={(e) => setTitle(e.target.value)}
                      disabled={loading}
                      className="flex-1 h-12 text-base bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-700 focus:border-blue-500 focus:ring-blue-500"
                    />
                    <Button
                      type="submit"
                      disabled={loading || !title.trim()}
                      className="h-12 px-6 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-lg shadow-blue-500/25 hover:shadow-xl hover:shadow-blue-500/40 transition-all"
                    >
                      {loading ? (
                        <Loader2 className="h-5 w-5 animate-spin" />
                      ) : (
                        <>
                          <Plus className="h-5 w-5 mr-2" />
                          Add
                        </>
                      )}
                    </Button>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <Input
                      type="text"
                      placeholder="Description (optional)"
                      value={description}
                      onChange={(e) => setDescription(e.target.value)}
                      disabled={loading}
                      className="h-10 text-sm bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-700 focus:border-blue-500 focus:ring-blue-500"
                    />
                    <Input
                      type="datetime-local"
                      value={dueDate}
                      onChange={(e) => setDueDate(e.target.value)}
                      disabled={loading}
                      className="h-10 text-sm bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-700 focus:border-blue-500 focus:ring-blue-500"
                    />
                  </div>
                </form>
              </CardContent>
            </Card>
          </motion.div>

          {/* Filter Tabs */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="mb-6"
          >
            <div className="flex gap-2 bg-white/80 dark:bg-gray-900/80 backdrop-blur-lg p-1 rounded-lg border border-gray-200 dark:border-gray-800 shadow-lg w-fit">
              <button
                onClick={() => {
                  console.log("Clicked: All");
                  setFilter("all");
                }}
                className={`px-6 py-2 rounded-md text-sm font-medium transition-all ${
                  filter === "all"
                    ? "bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-md"
                    : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
                }`}
              >
                <Circle className="h-4 w-4 inline mr-2" />
                All ({tasks.length})
              </button>
              <button
                onClick={() => {
                  console.log("Clicked: Active");
                  setFilter("active");
                }}
                className={`px-6 py-2 rounded-md text-sm font-medium transition-all ${
                  filter === "active"
                    ? "bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-md"
                    : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
                }`}
              >
                <Clock className="h-4 w-4 inline mr-2" />
                Active ({stats.active})
              </button>
              <button
                onClick={() => {
                  console.log("Clicked: Completed");
                  setFilter("completed");
                }}
                className={`px-6 py-2 rounded-md text-sm font-medium transition-all ${
                  filter === "completed"
                    ? "bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-md"
                    : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
                }`}
              >
                <CheckCheck className="h-4 w-4 inline mr-2" />
                Completed ({stats.completed})
              </button>
            </div>
          </motion.div>

          {/* Tasks List */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            className="space-y-3"
          >
            {initialLoading ? (
              <>
                <TaskSkeleton />
                <TaskSkeleton />
                <TaskSkeleton />
              </>
            ) : filteredTasks.length === 0 ? (
              <EmptyState />
            ) : (
              <div className="space-y-3">
                <motion.div
                  variants={stagger}
                  initial="initial"
                  animate="animate"
                  className="space-y-3"
                >
                  {filteredTasks.map((task) => (
                    <motion.div
                      key={task.id}
                      variants={fadeIn}
                      layout
                    >
                      <TaskItem task={task} onRefresh={fetchTasks} />
                    </motion.div>
                  ))}
                </motion.div>
              </div>
            )}
          </motion.div>
        </main>
      </div>
    </ProtectedRoute>
  );
}
