---
name: frontend-ui-generator
description: "Generate responsive Next.js UI components for AI chatbot interfaces with App Router, Tailwind CSS, and Better Auth integration. Use when building chat windows, task lists, auth forms, or any Todo-related UI components that need to be mobile-friendly and accessible."
category: Frontend / UI Generation
complexity: Medium
phase: 3
dependencies: ["Next.js 16+", "Tailwind CSS", "shadcn/ui", "Better Auth"]
---

# Skill: Frontend UI Generator

**Category**: Frontend / UI Generation
**Complexity**: Medium
**Phase**: 3 (AI-Powered Chatbot)
**Dependencies**: Next.js 16+, Tailwind CSS, shadcn/ui, Better Auth

## Purpose

Generate responsive Next.js UI components for AI chatbot interfaces with proper state management, authentication integration, and accessibility compliance.

## When to Use

- Building responsive ChatKit UIs for Todo interactions
- Creating custom chat windows or message displays
- Generating task list views and task cards
- Building authentication forms (login/signup)
- Creating loading states and error boundaries
- Implementing responsive layouts for mobile/desktop

## Pattern

### 1. Chat UI Component

```typescript
// frontend/components/chat/ChatUI.tsx
'use client';

import { useState, useEffect, useRef } from 'react';
import { Send, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { cn } from '@/lib/utils';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface ChatUIProps {
  messages: Message[];
  onSendMessage: (message: string) => Promise<void>;
  isLoading?: boolean;
  placeholder?: string;
  className?: string;
}

export function ChatUI({
  messages,
  onSendMessage,
  isLoading = false,
  placeholder = "Type your message...",
  className
}: ChatUIProps) {
  const [input, setInput] = useState('');
  const [isSending, setIsSending] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isSending) return;

    setIsSending(true);
    try {
      await onSendMessage(input);
      setInput('');
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setIsSending(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className={cn("flex flex-col h-full bg-white rounded-lg shadow-sm", className)}>
      {/* Messages Area */}
      <ScrollArea className="flex-1 p-4">
        <div className="space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={cn(
                "flex w-full",
                message.role === 'user' ? 'justify-end' : 'justify-start'
              )}
            >
              <div
                className={cn(
                  "max-w-[75%] rounded-2xl px-4 py-3 break-words",
                  message.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-900'
                )}
              >
                <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                <span className="text-xs opacity-70 mt-1 block">
                  {message.timestamp.toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </span>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 rounded-2xl px-4 py-3">
                <Loader2 className="w-5 h-5 animate-spin text-gray-600" />
              </div>
            </div>
          )}
          <div ref={scrollRef} />
        </div>
      </ScrollArea>

      {/* Input Area */}
      <div className="border-t p-4">
        <div className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={isSending}
            className="flex-1"
            aria-label="Message input"
          />
          <Button
            onClick={handleSend}
            disabled={!input.trim() || isSending}
            size="icon"
            aria-label="Send message"
          >
            {isSending ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
```

### 2. Task List Component

```typescript
// frontend/components/tasks/TaskList.tsx
'use client';

import { CheckCircle2, Circle, Trash2, Edit, Clock } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { cn } from '@/lib/utils';

interface Task {
  id: number;
  title: string;
  description?: string;
  completed: boolean;
  created_at: string;
}

interface TaskListProps {
  tasks: Task[];
  onToggleComplete?: (taskId: number) => void;
  onDelete?: (taskId: number) => void;
  onEdit?: (taskId: number) => void;
  emptyMessage?: string;
  className?: string;
}

export function TaskList({
  tasks,
  onToggleComplete,
  onDelete,
  onEdit,
  emptyMessage = "No tasks yet. Start by adding one!",
  className
}: TaskListProps) {
  if (tasks.length === 0) {
    return (
      <div className={cn("text-center py-12 text-gray-500", className)}>
        <Circle className="w-16 h-16 mx-auto mb-4 opacity-20" />
        <p>{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className={cn("space-y-3", className)}>
      {tasks.map((task) => (
        <Card
          key={task.id}
          className={cn(
            "p-4 transition-all hover:shadow-md",
            task.completed && "opacity-60"
          )}
        >
          <div className="flex items-start gap-3">
            {/* Complete Toggle */}
            <button
              onClick={() => onToggleComplete?.(task.id)}
              className="mt-1 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded"
              aria-label={task.completed ? "Mark as incomplete" : "Mark as complete"}
            >
              {task.completed ? (
                <CheckCircle2 className="w-5 h-5 text-green-600" />
              ) : (
                <Circle className="w-5 h-5 text-gray-400" />
              )}
            </button>

            {/* Task Content */}
            <div className="flex-1 min-w-0">
              <h3
                className={cn(
                  "font-medium text-gray-900",
                  task.completed && "line-through text-gray-500"
                )}
              >
                {task.title}
              </h3>
              {task.description && (
                <p className="text-sm text-gray-600 mt-1">{task.description}</p>
              )}
              <div className="flex items-center gap-1 mt-2 text-xs text-gray-500">
                <Clock className="w-3 h-3" />
                <span>
                  {new Date(task.created_at).toLocaleDateString([], {
                    month: 'short',
                    day: 'numeric',
                    year: 'numeric'
                  })}
                </span>
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-1">
              {onEdit && (
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => onEdit(task.id)}
                  aria-label="Edit task"
                >
                  <Edit className="w-4 h-4" />
                </Button>
              )}
              {onDelete && (
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => onDelete(task.id)}
                  className="text-red-600 hover:text-red-700 hover:bg-red-50"
                  aria-label="Delete task"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              )}
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
}
```

### 3. Authentication Form

```typescript
// frontend/components/auth/LoginForm.tsx
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2 } from 'lucide-react';
import { login } from '@/lib/auth';

export function LoginForm() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await login(email, password);
      router.push('/chat');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 w-full max-w-md">
      <div className="space-y-2">
        <Label htmlFor="email">Email</Label>
        <Input
          id="email"
          type="email"
          placeholder="you@example.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          disabled={isLoading}
          aria-required="true"
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="password">Password</Label>
        <Input
          id="password"
          type="password"
          placeholder="••••••••"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          disabled={isLoading}
          aria-required="true"
        />
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <Button
        type="submit"
        className="w-full"
        disabled={isLoading}
      >
        {isLoading ? (
          <>
            <Loader2 className="mr-2 w-4 h-4 animate-spin" />
            Logging in...
          </>
        ) : (
          'Log In'
        )}
      </Button>
    </form>
  );
}
```

### 4. Loading State Component

```typescript
// frontend/components/ui/LoadingState.tsx
import { Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface LoadingStateProps {
  message?: string;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

export function LoadingState({
  message = 'Loading...',
  className,
  size = 'md'
}: LoadingStateProps) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12'
  };

  return (
    <div className={cn("flex flex-col items-center justify-center py-12", className)}>
      <Loader2 className={cn("animate-spin text-blue-600 mb-4", sizeClasses[size])} />
      <p className="text-sm text-gray-600">{message}</p>
    </div>
  );
}
```

### 5. Integration with Page

```typescript
// frontend/app/chat/page.tsx
'use client';

import { useState, useEffect } from 'react';
import { ChatUI } from '@/components/chat/ChatUI';
import { TaskList } from '@/components/tasks/TaskList';
import { LoadingState } from '@/components/ui/LoadingState';
import { sendChatMessage, getTasks } from '@/lib/api';
import { useAuth } from '@/hooks/useAuth';

export default function ChatPage() {
  const { user, isLoading: authLoading } = useAuth();
  const [messages, setMessages] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (user) {
      loadTasks();
    }
  }, [user]);

  const loadTasks = async () => {
    try {
      const taskData = await getTasks(user.id);
      setTasks(taskData);
    } catch (error) {
      console.error('Failed to load tasks:', error);
    }
  };

  const handleSendMessage = async (message: string) => {
    // Add user message
    const userMessage = {
      id: Date.now().toString(),
      role: 'user' as const,
      content: message,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);

    setIsLoading(true);
    try {
      const response = await sendChatMessage(user.id, message);

      // Add assistant response
      const assistantMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant' as const,
        content: response.response,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, assistantMessage]);

      // Refresh tasks if tool was invoked
      if (response.tool_calls.length > 0) {
        await loadTasks();
      }
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (authLoading) {
    return <LoadingState message="Loading your workspace..." />;
  }

  return (
    <div className="flex h-screen">
      {/* Chat Section */}
      <div className="flex-1 p-6">
        <ChatUI
          messages={messages}
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
          placeholder="Ask me to add tasks, show your list, or mark items complete..."
        />
      </div>

      {/* Task List Sidebar */}
      <div className="w-96 border-l p-6 overflow-y-auto">
        <h2 className="text-xl font-bold mb-4">Your Tasks</h2>
        <TaskList
          tasks={tasks}
          onToggleComplete={async (id) => {
            await sendChatMessage(user.id, `Mark task ${id} as complete`);
            await loadTasks();
          }}
          onDelete={async (id) => {
            await sendChatMessage(user.id, `Delete task ${id}`);
            await loadTasks();
          }}
        />
      </div>
    </div>
  );
}
```

## Acceptance Criteria

- [ ] All components are fully responsive (mobile, tablet, desktop)
- [ ] WCAG 2.1 AA accessibility compliance (aria-labels, keyboard navigation)
- [ ] Loading states for all async operations
- [ ] Error states with user-friendly messages
- [ ] Proper TypeScript typing for all props
- [ ] Optimistic UI updates where appropriate
- [ ] Auto-scroll in chat on new messages
- [ ] Keyboard shortcuts (Enter to send, Escape to clear)
- [ ] Dark mode support (optional but recommended)

## Quality Criteria

### Responsiveness
- Mobile-first design approach
- Breakpoints: sm (640px), md (768px), lg (1024px), xl (1280px)
- Touch-friendly targets (min 44x44px)
- Proper text sizing and spacing

### Accessibility
- Semantic HTML elements
- ARIA labels and roles
- Keyboard navigation support
- Focus visible states
- Screen reader compatibility
- Color contrast ratios (4.5:1 minimum)

### Performance
- Lazy load images and heavy components
- Debounce input handlers
- Virtual scrolling for long lists
- Memoize expensive computations
- Code splitting for routes

## Testing

```typescript
// __tests__/ChatUI.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ChatUI } from '@/components/chat/ChatUI';

describe('ChatUI', () => {
  it('sends message on Enter key', async () => {
    const mockSend = jest.fn().mockResolvedValue(undefined);
    render(
      <ChatUI
        messages={[]}
        onSendMessage={mockSend}
      />
    );

    const input = screen.getByPlaceholderText(/type your message/i);
    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.keyDown(input, { key: 'Enter' });

    await waitFor(() => {
      expect(mockSend).toHaveBeenCalledWith('Test message');
    });
  });

  it('displays messages correctly', () => {
    const messages = [
      { id: '1', role: 'user', content: 'Hello', timestamp: new Date() },
      { id: '2', role: 'assistant', content: 'Hi!', timestamp: new Date() }
    ];

    render(<ChatUI messages={messages} onSendMessage={jest.fn()} />);

    expect(screen.getByText('Hello')).toBeInTheDocument();
    expect(screen.getByText('Hi!')).toBeInTheDocument();
  });

  it('disables input while sending', async () => {
    const mockSend = jest.fn().mockResolvedValue(undefined);
    render(<ChatUI messages={[]} onSendMessage={mockSend} />);

    const input = screen.getByPlaceholderText(/type your message/i);
    const button = screen.getByLabelText(/send message/i);

    fireEvent.change(input, { target: { value: 'Test' } });
    fireEvent.click(button);

    expect(input).toBeDisabled();
  });
});
```

## Common Issues

1. **Hydration errors**: Ensure timestamps/dates are handled consistently
2. **Memory leaks**: Clean up event listeners and subscriptions
3. **Scroll issues**: Use refs and scroll into view on updates
4. **State race conditions**: Use proper async/await patterns
5. **Z-index conflicts**: Follow consistent layering strategy

## Best Practices

1. **Component Structure**:
   - Keep components focused and single-responsibility
   - Extract reusable logic into custom hooks
   - Use composition over prop drilling

2. **State Management**:
   - Lift state only when necessary
   - Use context for global state
   - Optimize re-renders with memo/callback

3. **Styling**:
   - Use Tailwind utility classes
   - Extract repeated patterns into components
   - Follow consistent spacing scale

4. **Error Handling**:
   - Always handle async errors
   - Show user-friendly error messages
   - Provide recovery actions

## References

- [Next.js App Router Documentation](https://nextjs.org/docs/app)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [shadcn/ui Components](https://ui.shadcn.com/)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- Phase 3 Spec: `specs/phase3/frontend-ui.md`
- Related Skills: `chatkit.frontend.integration.md`, `auth.jwt.stateless.md`

## Version

1.0.0 - Initial Phase 3 implementation
