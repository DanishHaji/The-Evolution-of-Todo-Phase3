"use client";

import { ListTodo, Sparkles, CheckCircle2, Target } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { motion } from "framer-motion";

export function EmptyState() {
  return (
    <Card className="border-2 border-dashed border-gray-300 dark:border-gray-700 bg-gradient-to-br from-blue-50/50 to-purple-50/50 dark:from-gray-900/50 dark:to-gray-800/50">
      <CardContent className="flex flex-col items-center justify-center py-20">
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5, type: "spring" }}
          className="relative mb-6"
        >
          <div className="absolute inset-0 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full blur-xl opacity-20 animate-pulse" />
          <div className="relative h-24 w-24 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-2xl">
            <ListTodo className="h-12 w-12 text-white" />
          </div>
        </motion.div>

        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="text-center"
        >
          <h3 className="text-2xl font-bold mb-3 bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent dark:from-white dark:to-gray-300">
            No tasks yet - Let's get started! 🚀
          </h3>
          <p className="text-base text-gray-600 dark:text-gray-400 max-w-md mx-auto mb-6">
            Create your first task above and start your journey to better productivity
          </p>
        </motion.div>

        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6 max-w-2xl"
        >
          <div className="flex items-start gap-3 p-4 rounded-lg bg-white/50 dark:bg-gray-800/50">
            <div className="h-10 w-10 rounded-lg bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center flex-shrink-0">
              <Target className="h-5 w-5 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <h4 className="font-semibold text-sm text-gray-900 dark:text-white mb-1">
                Set Goals
              </h4>
              <p className="text-xs text-gray-600 dark:text-gray-400">
                Break down your goals into actionable tasks
              </p>
            </div>
          </div>

          <div className="flex items-start gap-3 p-4 rounded-lg bg-white/50 dark:bg-gray-800/50">
            <div className="h-10 w-10 rounded-lg bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center flex-shrink-0">
              <CheckCircle2 className="h-5 w-5 text-purple-600 dark:text-purple-400" />
            </div>
            <div>
              <h4 className="font-semibold text-sm text-gray-900 dark:text-white mb-1">
                Track Progress
              </h4>
              <p className="text-xs text-gray-600 dark:text-gray-400">
                Check off tasks as you complete them
              </p>
            </div>
          </div>

          <div className="flex items-start gap-3 p-4 rounded-lg bg-white/50 dark:bg-gray-800/50">
            <div className="h-10 w-10 rounded-lg bg-green-100 dark:bg-green-900/30 flex items-center justify-center flex-shrink-0">
              <Sparkles className="h-5 w-5 text-green-600 dark:text-green-400" />
            </div>
            <div>
              <h4 className="font-semibold text-sm text-gray-900 dark:text-white mb-1">
                Stay Organized
              </h4>
              <p className="text-xs text-gray-600 dark:text-gray-400">
                Keep all your tasks in one beautiful place
              </p>
            </div>
          </div>
        </motion.div>
      </CardContent>
    </Card>
  );
}
