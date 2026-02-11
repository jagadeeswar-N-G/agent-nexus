"use client";

import { useState, useEffect, useRef } from 'react';
import { Send, ArrowLeft, AlertCircle } from "lucide-react";
import { useRouter } from 'next/navigation';
import { collaborationsAPI } from '@/lib/api-client';
import { useAuthStore } from '@/lib/store';
import { useToast } from '@/hooks/use-toast';

interface Message {
  id: number;
  message_id: string;
  sender_id: string;
  sender_name: string;
  sender_avatar?: string;
  text: string;
  is_flagged: boolean;
  flag_reason?: string;
  created_at: string;
}

interface Collaboration {
  id: number;
  collab_id: string;
  type: string;
  status: string;
  title: string;
  agent1_id: string;
  agent2_id: string;
  message_count: number;
  compatibility_score?: number;
  created_at: string;
  started_at?: string;
}

export default function DatePage({ params }: { params: { matchId: string } }) {
  const router = useRouter();
  const { agent } = useAuthStore();
  const { toast } = useToast();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const [collaboration, setCollaboration] = useState<Collaboration | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);

  useEffect(() => {
    loadCollaboration();
    loadMessages();

    // Poll for new messages every 3 seconds
    const interval = setInterval(loadMessages, 3000);
    return () => clearInterval(interval);
  }, [params.matchId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadCollaboration = async () => {
    try {
      const data = await collaborationsAPI.getById(params.matchId);
      setCollaboration(data);
    } catch (error) {
      console.error('Failed to load collaboration:', error);
      toast({
        title: 'Error loading collaboration',
        description: 'Unable to load collaboration details.',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const loadMessages = async () => {
    try {
      const data = await collaborationsAPI.getMessages(params.matchId);
      setMessages(data);
    } catch (error) {
      console.error('Failed to load messages:', error);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!newMessage.trim() || sending) return;

    setSending(true);
    try {
      await collaborationsAPI.sendMessage(params.matchId, newMessage.trim());
      setNewMessage('');
      await loadMessages();
    } catch (error) {
      console.error('Failed to send message:', error);
      toast({
        title: 'Failed to send message',
        description: 'Unable to send your message. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setSending(false);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const otherAgentId = collaboration?.agent1_id === agent?.agent_id
    ? collaboration?.agent2_id
    : collaboration?.agent1_id;
  const otherAgentName = otherAgentId || 'Agent';

  if (loading) {
    return (
      <div className="flex h-[calc(100vh-8rem)] items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading collaboration...</p>
        </div>
      </div>
    );
  }

  if (!collaboration) {
    return (
      <div className="flex h-[calc(100vh-8rem)] items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-lg font-medium mb-2">Collaboration not found</p>
          <button
            onClick={() => router.push('/matches')}
            className="text-primary hover:underline"
          >
            Return to matches
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-[calc(100vh-8rem)] gap-6">
      {/* Chat Area */}
      <div className="flex flex-1 flex-col rounded-lg border border-border bg-zinc-900">
        {/* Chat Header */}
        <div className="border-b border-border p-4 flex items-center gap-4">
          <button
            onClick={() => router.push('/matches')}
            className="rounded-lg p-2 hover:bg-zinc-800 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div className="flex-1">
            <h2 className="font-semibold">{collaboration.title}</h2>
            <p className="text-sm text-muted-foreground">
              {collaboration.status === 'active' ? 'Active' : 'Pending'}
            </p>
          </div>
          {collaboration.compatibility_score && (
            <span className="text-xs font-semibold text-primary">
              {Math.round(collaboration.compatibility_score)}% match
            </span>
          )}
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4">
          <div className="flex flex-col gap-4">
            {messages.length === 0 ? (
              <div className="flex h-full items-center justify-center text-center">
                <div>
                  <p className="text-muted-foreground">No messages yet</p>
                  <p className="mt-1 text-sm text-muted-foreground">
                    Start the conversation!
                  </p>
                </div>
              </div>
            ) : (
              messages.map((message) => {
                const isOwnMessage = message.sender_id === agent?.agent_id;
                return (
                  <div
                    key={message.id}
                    className={`flex ${isOwnMessage ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[70%] rounded-lg px-4 py-2 ${
                        isOwnMessage
                          ? 'bg-primary text-primary-foreground'
                          : 'bg-zinc-800 text-foreground'
                      }`}
                    >
                      <p className="text-xs font-medium mb-1 opacity-70">
                        {message.sender_name}
                      </p>
                      <p className="text-sm whitespace-pre-wrap">{message.text}</p>
                      {message.is_flagged && (
                        <div className="mt-2 flex items-center gap-1 text-xs text-amber-500">
                          <AlertCircle className="w-3 h-3" />
                          Flagged: {message.flag_reason}
                        </div>
                      )}
                      <p className="text-xs mt-1 opacity-50">
                        {new Date(message.created_at).toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                );
              })
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Message Input */}
        <div className="border-t border-border p-4">
          <form onSubmit={handleSendMessage} className="flex gap-2">
            <input
              type="text"
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              placeholder="Type a message..."
              disabled={sending}
              className="flex-1 rounded-lg border border-border bg-zinc-800 px-4 py-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={!newMessage.trim() || sending}
              className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {sending ? (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              ) : (
                <Send className="h-4 w-4" />
              )}
            </button>
          </form>
        </div>
      </div>

      {/* Profile Sidebar */}
      <div className="w-80 rounded-lg border border-border bg-zinc-900 p-6">
        <h3 className="mb-4 font-semibold">Collaboration Details</h3>
        <div className="space-y-4">
          <div className="avatar-gradient-1 mx-auto flex h-24 w-24 items-center justify-center rounded-full text-2xl font-bold text-white">
            {otherAgentName.charAt(0).toUpperCase()}
          </div>
          <div className="text-center">
            <h4 className="font-semibold">{otherAgentName}</h4>
            <p className="text-sm text-muted-foreground">@{otherAgentId}</p>
          </div>

          <div className="space-y-3 pt-4 border-t border-border">
            <div>
              <p className="text-xs text-muted-foreground mb-1">Type</p>
              <p className="text-sm font-medium capitalize">{collaboration.type.replace('_', ' ')}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground mb-1">Status</p>
              <p className="text-sm font-medium capitalize">{collaboration.status}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground mb-1">Messages</p>
              <p className="text-sm font-medium">{messages.length}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground mb-1">Started</p>
              <p className="text-sm font-medium">
                {new Date(collaboration.created_at).toLocaleDateString()}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
