"use client";

import React, { useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { api } from "@/lib/api";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { CheckCircle2, Mail, Lock, Loader2, ArrowRight, Sparkles, ShieldCheck } from "lucide-react";
import { toast } from "sonner";
import { motion } from "framer-motion";

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();

    if (password !== confirmPassword) {
      toast.error("Passwords don't match", {
        description: "Please make sure both passwords are identical.",
      });
      return;
    }

    if (password.length < 6) {
      toast.error("Password too short", {
        description: "Password must be at least 6 characters long.",
      });
      return;
    }

    setLoading(true);

    try {
      const data = await api.post("/api/auth/register", { email, password }) as { token: string; user: any };
      toast.success("Account created! 🎉", {
        description: "Welcome to TaskFlow! Let's get organized.",
      });
      login(data.token, data.user);
    } catch (err: any) {
      toast.error("Registration failed", {
        description: err.message || "Could not create your account. Please try again.",
      });
    } finally {
      setLoading(false);
    }
  };

  const fadeIn = {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.5 }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-900 dark:to-purple-950 p-4">
      {/* Background Pattern */}
      <div className="absolute inset-0 bg-grid-slate-100 [mask-image:linear-gradient(0deg,white,rgba(255,255,255,0.6))] dark:bg-grid-slate-700/25 dark:[mask-image:linear-gradient(0deg,rgba(255,255,255,0.1),rgba(255,255,255,0.5))]" />

      {/* Decorative Elements */}
      <div className="absolute left-1/4 top-1/4 h-72 w-72 rounded-full bg-purple-300 opacity-20 blur-3xl dark:bg-purple-800" />
      <div className="absolute bottom-1/4 right-1/4 h-72 w-72 rounded-full bg-blue-300 opacity-20 blur-3xl dark:bg-blue-800" />

      <div className="relative max-w-md w-full">
        {/* Logo and Brand */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="flex flex-col items-center mb-8"
        >
          <Link href="/" className="flex items-center gap-2 mb-4 group">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 shadow-lg shadow-blue-500/30 group-hover:shadow-xl group-hover:shadow-blue-500/40 transition-all">
              <CheckCircle2 className="h-7 w-7 text-white" />
            </div>
            <span className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent dark:from-blue-400 dark:to-purple-400">
              TaskFlow
            </span>
          </Link>
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="inline-flex items-center gap-2 rounded-full border border-purple-200 bg-purple-50 px-4 py-1.5 text-sm font-medium text-purple-700 dark:border-purple-800 dark:bg-purple-950 dark:text-purple-300"
          >
            <Sparkles className="h-4 w-4" />
            <span>Join thousands of productive users</span>
          </motion.div>
        </motion.div>

        {/* Register Card */}
        <motion.div variants={fadeIn} initial="initial" animate="animate">
          <Card className="border-2 border-gray-200 dark:border-gray-800 shadow-2xl bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl">
            <CardContent className="pt-8 pb-8 px-8">
              <div className="mb-6 text-center">
                <h1 className="text-3xl font-bold tracking-tight mb-2 bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent dark:from-white dark:to-gray-300">
                  Create Account
                </h1>
                <p className="text-gray-600 dark:text-gray-400">
                  Start your productivity journey today
                </p>
              </div>

              <form onSubmit={handleRegister} className="space-y-5">
                <div className="space-y-2">
                  <label className="text-sm font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                    <Mail className="h-4 w-4 text-gray-500" />
                    Email Address
                  </label>
                  <Input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@example.com"
                    className="h-12 bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-700 focus:border-blue-500 focus:ring-blue-500"
                    required
                    disabled={loading}
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                    <Lock className="h-4 w-4 text-gray-500" />
                    Password
                  </label>
                  <Input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="h-12 bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-700 focus:border-blue-500 focus:ring-blue-500"
                    required
                    disabled={loading}
                    minLength={6}
                  />
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Must be at least 6 characters long
                  </p>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                    <ShieldCheck className="h-4 w-4 text-gray-500" />
                    Confirm Password
                  </label>
                  <Input
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="••••••••"
                    className="h-12 bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-700 focus:border-blue-500 focus:ring-blue-500"
                    required
                    disabled={loading}
                    minLength={6}
                  />
                </div>

                <Button
                  type="submit"
                  disabled={loading}
                  className="w-full h-12 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white text-base font-semibold shadow-lg shadow-blue-500/25 hover:shadow-xl hover:shadow-blue-500/40 transition-all group"
                >
                  {loading ? (
                    <>
                      <Loader2 className="h-5 w-5 animate-spin mr-2" />
                      Creating Account...
                    </>
                  ) : (
                    <>
                      Create Account
                      <ArrowRight className="h-5 w-5 ml-2 transition-transform group-hover:translate-x-1" />
                    </>
                  )}
                </Button>
              </form>

              <div className="mt-6 text-center">
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Already have an account?{" "}
                  <Link
                    href="/login"
                    className="font-semibold text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 transition-colors"
                  >
                    Sign in instead →
                  </Link>
                </p>
              </div>

              <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-800">
                <p className="text-xs text-center text-gray-500 dark:text-gray-400">
                  By creating an account, you agree to our Terms of Service and Privacy Policy
                </p>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Bottom Link */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="mt-6 text-center"
        >
          <Link
            href="/"
            className="text-sm text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition-colors"
          >
            ← Back to Home
          </Link>
        </motion.div>
      </div>
    </div>
  );
}
