"use client"

import Link from "next/link"
import { motion } from "framer-motion"
import { ArrowRight, CheckCircle2, Sparkles, Zap, Shield, BarChart3 } from "lucide-react"
import { useAuth } from "@/context/AuthContext"
import { useRouter } from "next/navigation"
import { useEffect } from "react"

export default function Home() {
  const { user, loading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!loading && user) {
      router.push("/dashboard")
    }
  }, [user, loading, router])

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-lg">Loading...</div>
      </div>
    )
  }

  const fadeIn = {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.6 }
  }

  const stagger = {
    animate: {
      transition: {
        staggerChildren: 0.1
      }
    }
  }

  return (
    <div className="flex min-h-screen flex-col">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-900 dark:to-purple-950">
        {/* Background Pattern */}
        <div className="absolute inset-0 bg-grid-slate-100 [mask-image:linear-gradient(0deg,white,rgba(255,255,255,0.6))] dark:bg-grid-slate-700/25 dark:[mask-image:linear-gradient(0deg,rgba(255,255,255,0.1),rgba(255,255,255,0.5))]" />

        <div className="relative">
          {/* Navigation */}
          <nav className="container mx-auto flex items-center justify-between px-6 py-6">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5 }}
              className="flex items-center gap-2"
            >
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-purple-600">
                <CheckCircle2 className="h-6 w-6 text-white" />
              </div>
              <span className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent dark:from-blue-400 dark:to-purple-400">
                TaskFlow
              </span>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5 }}
              className="flex items-center gap-4"
            >
              <Link
                href="/login"
                className="text-sm font-medium text-gray-700 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white transition-colors"
              >
                Sign In
              </Link>
              <Link
                href="/register"
                className="rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 px-6 py-2.5 text-sm font-semibold text-white shadow-lg shadow-blue-500/25 transition-all hover:shadow-xl hover:shadow-blue-500/40 hover:scale-105"
              >
                Get Started Free
              </Link>
            </motion.div>
          </nav>

          {/* Hero Content */}
          <div className="container mx-auto px-6 pb-24 pt-16 md:pb-32 md:pt-24">
            <motion.div
              variants={stagger}
              initial="initial"
              animate="animate"
              className="mx-auto max-w-4xl text-center"
            >
              <motion.div
                variants={fadeIn}
                className="mb-6 inline-flex items-center gap-2 rounded-full border border-blue-200 bg-blue-50 px-4 py-1.5 text-sm font-medium text-blue-700 dark:border-blue-800 dark:bg-blue-950 dark:text-blue-300"
              >
                <Sparkles className="h-4 w-4" />
                <span>Now with AI-powered task suggestions</span>
              </motion.div>

              <motion.h1
                variants={fadeIn}
                className="mb-6 bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 bg-clip-text text-5xl font-bold leading-tight tracking-tight text-transparent dark:from-white dark:via-gray-100 dark:to-gray-300 md:text-6xl lg:text-7xl"
              >
                Organize Your Life,
                <br />
                One Task at a Time
              </motion.h1>

              <motion.p
                variants={fadeIn}
                className="mb-10 text-lg leading-relaxed text-gray-600 dark:text-gray-400 md:text-xl"
              >
                The most beautiful and powerful way to manage your tasks. Stay organized, boost productivity, and achieve your goals with TaskFlow.
              </motion.p>

              <motion.div
                variants={fadeIn}
                className="flex flex-col items-center justify-center gap-4 sm:flex-row"
              >
                <Link
                  href="/register"
                  className="group inline-flex items-center gap-2 rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 px-8 py-4 text-base font-semibold text-white shadow-2xl shadow-blue-500/25 transition-all hover:shadow-2xl hover:shadow-blue-500/40 hover:scale-105"
                >
                  Start For Free
                  <ArrowRight className="h-5 w-5 transition-transform group-hover:translate-x-1" />
                </Link>
                <Link
                  href="#features"
                  className="inline-flex items-center gap-2 rounded-lg border-2 border-gray-300 bg-white px-8 py-4 text-base font-semibold text-gray-700 transition-all hover:border-gray-400 hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300 dark:hover:border-gray-600 dark:hover:bg-gray-700"
                >
                  Learn More
                </Link>
              </motion.div>

              <motion.p
                variants={fadeIn}
                className="mt-6 text-sm text-gray-500 dark:text-gray-500"
              >
                No credit card required · Free forever · Cancel anytime
              </motion.p>
            </motion.div>
          </div>
        </div>

        {/* Decorative Elements */}
        <div className="absolute left-1/4 top-1/4 h-72 w-72 rounded-full bg-purple-300 opacity-20 blur-3xl dark:bg-purple-800" />
        <div className="absolute bottom-1/4 right-1/4 h-72 w-72 rounded-full bg-blue-300 opacity-20 blur-3xl dark:bg-blue-800" />
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 bg-white dark:bg-gray-900">
        <div className="container mx-auto px-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="mx-auto max-w-3xl text-center mb-16"
          >
            <h2 className="mb-4 text-4xl font-bold md:text-5xl">
              Everything You Need to
              <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent"> Stay Organized</span>
            </h2>
            <p className="text-lg text-gray-600 dark:text-gray-400">
              Powerful features designed to help you manage tasks effortlessly and boost your productivity.
            </p>
          </motion.div>

          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="group relative overflow-hidden rounded-2xl border border-gray-200 bg-white p-8 shadow-sm transition-all hover:shadow-xl dark:border-gray-800 dark:bg-gray-800"
              >
                <div className="mb-4 inline-flex h-14 w-14 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 text-white shadow-lg">
                  {feature.icon}
                </div>
                <h3 className="mb-3 text-xl font-semibold text-gray-900 dark:text-white">
                  {feature.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  {feature.description}
                </p>
                <div className="absolute right-6 top-6 opacity-0 transition-opacity group-hover:opacity-100">
                  <ArrowRight className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-gradient-to-br from-blue-600 to-purple-600">
        <div className="container mx-auto px-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="mx-auto max-w-3xl text-center"
          >
            <h2 className="mb-6 text-4xl font-bold text-white md:text-5xl">
              Ready to Get Organized?
            </h2>
            <p className="mb-10 text-lg text-blue-100 md:text-xl">
              Join thousands of users who are already managing their tasks better with TaskFlow.
            </p>
            <Link
              href="/register"
              className="inline-flex items-center gap-2 rounded-lg bg-white px-8 py-4 text-base font-semibold text-blue-600 shadow-2xl transition-all hover:bg-gray-50 hover:scale-105"
            >
              Get Started Now
              <ArrowRight className="h-5 w-5" />
            </Link>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-200 bg-white py-12 dark:border-gray-800 dark:bg-gray-900">
        <div className="container mx-auto px-6">
          <div className="flex flex-col items-center justify-between gap-4 md:flex-row">
            <div className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-purple-600">
                <CheckCircle2 className="h-5 w-5 text-white" />
              </div>
              <span className="text-lg font-bold text-gray-900 dark:text-white">TaskFlow</span>
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              © 2026 TaskFlow. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}

const features = [
  {
    icon: <Zap className="h-7 w-7" />,
    title: "Lightning Fast",
    description: "Experience blazing fast performance with our optimized task management system. No lag, just pure productivity.",
  },
  {
    icon: <Shield className="h-7 w-7" />,
    title: "Secure & Private",
    description: "Your data is encrypted and secure. We never share your information with third parties. Your privacy is our priority.",
  },
  {
    icon: <BarChart3 className="h-7 w-7" />,
    title: "Track Progress",
    description: "Visualize your productivity with beautiful charts and insights. See how you're improving over time.",
  },
  {
    icon: <CheckCircle2 className="h-7 w-7" />,
    title: "Smart Organization",
    description: "Organize tasks by priority, category, and due date. Never miss a deadline with intelligent reminders.",
  },
  {
    icon: <Sparkles className="h-7 w-7" />,
    title: "Beautiful Design",
    description: "Enjoy a stunning interface that makes task management a pleasure. Dark mode included for late-night productivity.",
  },
  {
    icon: <ArrowRight className="h-7 w-7" />,
    title: "Seamless Sync",
    description: "Access your tasks from anywhere. Real-time synchronization across all your devices keeps you in sync.",
  },
]
