---
name: chatkit.frontend.integration
description: "Integrate OpenAI ChatKit into the Next.js frontend to provide a conversational interface for todo management. Use when building the chat UI for Phase 3, implementing message sending/receiving, configuring ChatKit authentication, or customizing chat appearance."
category: Frontend / ChatKit
complexity: Medium
phase: 3
dependencies: ["OpenAI ChatKit", "Next.js 16+", "TypeScript"]
---

# Skill: OpenAI ChatKit Frontend Integration

**Category**: Frontend / ChatKit
**Complexity**: Medium
**Phase**: 3 (AI-Powered Chatbot)
**Dependencies**: OpenAI ChatKit, Next.js 16+

## Purpose

Integrate OpenAI ChatKit into the Next.js frontend to provide a conversational interface for todo management.

## When to Use

- Building the chat UI for Phase 3
- Implementing message sending/receiving
- Configuring ChatKit authentication
- Customizing chat appearance

## Pattern

### 1. ChatKit Configuration

```typescript
// frontend/lib/chatkit-config.ts
import { ChatKitConfig } from '@openai/chatkit';

export const chatKitConfig: ChatKitConfig = {
  // Domain key from OpenAI Platform
  domainKey: process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY!,

  // API endpoint for chat
  apiEndpoint: `${process.env.NEXT_PUBLIC_API_URL}/api`,

  // Authentication
  getAuthToken: async () => {
    // Return JWT from local storage or cookie
    const token = localStorage.getItem('access_token');
    return token || '';
  },

  // Custom headers for API requests
  getHeaders: async () => {
    const token = localStorage.getItem('access_token');
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };
  },

  // User info
  getUserId: async () => {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      const user = JSON.parse(userStr);
      return user.id;
    }
    return null;
  },

  // Chat configuration
  initialMessages: [
    {
      role: 'assistant',
      content: 'Hi! I\'m your todo assistant. You can ask me to add tasks, show your tasks, mark them complete, or delete them. How can I help you today?'
    }
  ],

  // Styling
  theme: {
    primaryColor: '#3b82f6',
    backgroundColor: '#ffffff',
    messageBackgroundColor: '#f3f4f6',
    userMessageBackgroundColor: '#3b82f6',
    borderRadius: '12px',
    fontFamily: 'system-ui, -apple-system, sans-serif'
  }
};
```

### 2. Chat Page Implementation

```typescript
// frontend/app/chat/page.tsx
'use client';

import { useState, useEffect } from 'react';
import { ChatKit } from '@openai/chatkit';
import { chatKitConfig } from '@/lib/chatkit-config';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { LogOut } from 'lucide-react';

export default function ChatPage() {
  const router = useRouter();
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Check authentication
    const token = localStorage.getItem('access_token');
    if (!token) {
      router.push('/login');
      return;
    }
    setIsAuthenticated(true);

    // Get or create conversation ID
    const savedConvId = localStorage.getItem('conversation_id');
    if (savedConvId) {
      setConversationId(parseInt(savedConvId));
    }
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    localStorage.removeItem('conversation_id');
    router.push('/login');
  };

  const handleMessageSent = (message: any) => {
    // Save conversation ID after first message
    if (message.conversation_id && !conversationId) {
      setConversationId(message.conversation_id);
      localStorage.setItem('conversation_id', message.conversation_id.toString());
    }
  };

  if (!isAuthenticated) {
    return <div>Loading...</div>;
  }

  return (
    <div className="flex flex-col h-screen">
      {/* Header */}
      <header className="border-b bg-white px-6 py-4">
        <div className="flex items-center justify-between max-w-4xl mx-auto">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Todo Assistant</h1>
            <p className="text-sm text-gray-600">Manage your tasks with AI</p>
          </div>
          <Button variant="outline" onClick={handleLogout}>
            <LogOut className="w-4 h-4 mr-2" />
            Logout
          </Button>
        </div>
      </header>

      {/* Chat Interface */}
      <main className="flex-1 overflow-hidden">
        <div className="max-w-4xl mx-auto h-full">
          <ChatKit
            config={chatKitConfig}
            conversationId={conversationId}
            onMessageSent={handleMessageSent}
            placeholder="Type your message... (e.g., 'Add a task to buy milk')"
            className="h-full"
          />
        </div>
      </main>
    </div>
  );
}
```

### 3. API Integration with Backend

```typescript
// frontend/lib/api.ts (updated for chat)
const API_BASE = process.env.NEXT_PUBLIC_API_URL;

interface ChatRequest {
  message: string;
  conversation_id?: number;
}

interface ChatResponse {
  conversation_id: number;
  response: string;
  tool_calls: Array<{
    tool: string;
    arguments: any;
    result: any;
  }>;
}

export async function sendChatMessage(
  userId: string,
  message: string,
  conversationId?: number
): Promise<ChatResponse> {
  const token = localStorage.getItem('access_token');

  const response = await fetch(`${API_BASE}/api/${userId}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      message,
      conversation_id: conversationId
    } as ChatRequest)
  });

  if (!response.ok) {
    if (response.status === 401) {
      // Token expired, try refresh
      throw new Error('Unauthorized');
    }
    throw new Error('Failed to send message');
  }

  return response.json();
}
```

### 4. Protected Route Wrapper

```typescript
// frontend/components/auth/ProtectedChatRoute.tsx
'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export function ProtectedChatRoute({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const checkAuth = () => {
      const token = localStorage.getItem('access_token');
      const user = localStorage.getItem('user');

      if (!token || !user) {
        router.push('/login');
        return;
      }

      setIsAuthenticated(true);
    };

    checkAuth();
  }, [router]);

  if (!isAuthenticated) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
```

### 5. Custom Message Renderer (Optional)

```typescript
// frontend/components/chat/CustomMessage.tsx
import { MessageProps } from '@openai/chatkit';
import { CheckCircle2, Circle, Trash2, Edit } from 'lucide-react';

export function CustomMessage({ message, isUser }: MessageProps) {
  // Parse tool calls from message metadata
  const toolCalls = message.metadata?.tool_calls || [];

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-[70%] rounded-2xl px-4 py-3 ${
          isUser
            ? 'bg-blue-600 text-white'
            : 'bg-gray-100 text-gray-900'
        }`}
      >
        <p className="whitespace-pre-wrap">{message.content}</p>

        {/* Show tool actions */}
        {toolCalls.length > 0 && (
          <div className="mt-2 pt-2 border-t border-gray-200/20">
            <p className="text-xs opacity-70 mb-1">Actions taken:</p>
            {toolCalls.map((call: any, idx: number) => (
              <div key={idx} className="flex items-center gap-2 text-xs">
                {call.tool === 'add_task' && <Circle className="w-3 h-3" />}
                {call.tool === 'complete_task' && <CheckCircle2 className="w-3 h-3" />}
                {call.tool === 'delete_task' && <Trash2 className="w-3 h-3" />}
                {call.tool === 'update_task' && <Edit className="w-3 h-3" />}
                <span>{call.tool.replace('_', ' ')}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
```

## Acceptance Criteria

- [ ] ChatKit initializes with correct domain key
- [ ] Messages sent to backend `/api/{user_id}/chat` endpoint
- [ ] JWT token included in Authorization header
- [ ] Conversation ID persisted across page reloads
- [ ] User redirected to login if not authenticated
- [ ] Chat interface is responsive (mobile + desktop)
- [ ] Initial welcome message displayed
- [ ] Loading states handled gracefully

## Domain Allowlist Setup

**IMPORTANT**: Before deploying, configure OpenAI domain allowlist:

1. Deploy frontend to get production URL
2. Go to: https://platform.openai.com/settings/organization/security/domain-allowlist
3. Add your domain (e.g., `https://your-app.vercel.app`)
4. Copy the domain key
5. Add to `.env`: `NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-key`

## Testing

```typescript
// Test chat API integration
describe('ChatKit Integration', () => {
  it('sends message to backend', async () => {
    const response = await sendChatMessage(
      'test-user',
      'Add a task to buy milk'
    );

    expect(response.conversation_id).toBeDefined();
    expect(response.response).toContain('task');
    expect(response.tool_calls.length).toBeGreaterThan(0);
  });

  it('handles authentication errors', async () => {
    localStorage.removeItem('access_token');

    await expect(
      sendChatMessage('test-user', 'Hello')
    ).rejects.toThrow('Unauthorized');
  });
});
```

## Common Issues

1. **Domain key error**: Ensure domain is added to OpenAI allowlist
2. **CORS issues**: Check backend CORS configuration allows frontend origin
3. **401 Unauthorized**: Token may be expired, implement refresh logic
4. **Message not sending**: Verify API endpoint URL is correct
5. **Conversation not persisting**: Check localStorage conversation_id

## Customization Options

- Theme colors via `theme` config
- Custom message renderer via `renderMessage` prop
- Custom input placeholder
- Welcome message customization
- Avatar images
- Typing indicators

## References

- [OpenAI ChatKit Documentation](https://platform.openai.com/docs/guides/chatkit)
- Phase 3 Spec: `specs/phase3/chatkit-ui.md`
- Related Skills: `auth.jwt.verify.md`, `conversation.persistence.md`

## Version

1.0.0 - Initial Phase 3 implementation
