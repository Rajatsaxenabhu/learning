import { useEffect, useRef, useState, useCallback } from 'react';
import { toast } from "react-toastify";

const BACKEND_BASE_URL = import.meta.env.VITE_API_URL ?? "";

function resolveSSEUrl(url: string): string {
  if (!url || /^https?:\/\//i.test(url)) return url;
  if (url.startsWith("/api")) return `${BACKEND_BASE_URL}${url}`;
  return url;
}

export function useSSE(url: string, options?: { reconnect?: boolean; withCredentials?: boolean }) {
  const sourceRef = useRef<EventSource | null>(null);
  const [messages, setMessages] = useState<string[]>([]);
  const [lastMessage, setLastMessage] = useState<string | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const reconnectInterval = useRef<ReturnType<typeof setTimeout> | null>(null);
  const reconnectEnabled = useRef(options?.reconnect ?? false);
  const withCredentials = options?.withCredentials ?? true;

  useEffect(() => {
    reconnectEnabled.current = options?.reconnect ?? false;
  }, [options?.reconnect]);

  useEffect(() => {
    setMessages([]);
    setLastMessage(null);
    setIsConnected(false);

    if (!url) return;

    if (sourceRef.current) {
      sourceRef.current.close();
      sourceRef.current = null;
    }

    if (reconnectInterval.current) {
      clearTimeout(reconnectInterval.current);
      reconnectInterval.current = null;
    }

    const source = new EventSource(resolveSSEUrl(url), { withCredentials });
    sourceRef.current = source;

    source.onopen = () => {
      setIsConnected(true);
    };

    source.onmessage = (event) => {
      if (typeof event.data === 'string') {
        setMessages((prev) => [...prev, event.data]);
        setLastMessage(event.data);
      }
    };

    source.onerror = () => {
      setIsConnected(false);
      if (source.readyState === EventSource.CLOSED) {
        sourceRef.current = null;
        if (reconnectEnabled.current && !reconnectInterval.current) {
          reconnectInterval.current = setTimeout(() => {
            reconnectInterval.current = null;
          }, 3000);
        } else if (!reconnectEnabled.current) {
          toast.error('SSE connection error');
        }
      }
    };

    return () => {
      if (reconnectInterval.current) {
        clearTimeout(reconnectInterval.current);
        reconnectInterval.current = null;
      }
      if (source.readyState !== EventSource.CLOSED) {
        source.close();
      }
      sourceRef.current = null;
    };
  }, [url]);

  const disconnect = useCallback(() => {
    reconnectEnabled.current = false;
    if (reconnectInterval.current) {
      clearTimeout(reconnectInterval.current);
      reconnectInterval.current = null;
    }
    if (sourceRef.current) {
      sourceRef.current.close();
      sourceRef.current = null;
    }
    setIsConnected(false);
    setMessages([]);
    setLastMessage(null);
  }, []);

  return {
    messages,
    lastMessage,
    isConnected,
    disconnect,
  };
}
