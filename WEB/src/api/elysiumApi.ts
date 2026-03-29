const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface SendMessageRequest {
  chat: string;
}

export const sendMessage = async (message: string): Promise<string> => {
  const response = await fetch(`${API_BASE_URL}/api/v1/chat/Agent`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ chat: message }),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  const data = await response.json();
  return data;
};

export const generateId = (): string => {
  return Math.random().toString(36).substring(2, 15);
};

export const getCurrentTimestamp = (): string => {
  const now = new Date();
  return now.toLocaleTimeString('en-US', { 
    hour: '2-digit', 
    minute: '2-digit',
    second: '2-digit',
    hour12: false 
  });
};
