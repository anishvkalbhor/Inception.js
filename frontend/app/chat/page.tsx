"use client";

import { useUser, useAuth } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import ChatInterface from "@/components/ChatInterface";

export default function ChatPage() {
  const { user, isLoaded } = useUser();
  const { getToken } = useAuth();
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [currentDocumentName, setCurrentDocumentName] = useState<string | null>(null);

  useEffect(() => {
    if (isLoaded && !user) {
      router.push("/");
    }
  }, [user, isLoaded, router]);

  useEffect(() => {
    const fetchToken = async () => {
      if (user) {
        const clerkToken = await getToken();
        setToken(clerkToken);
      }
    };
    fetchToken();
  }, [user, getToken]);

  if (!isLoaded) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500 mx-auto"></div>
          <p className="text-white mt-4">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user || !token) {
    return null;
  }

  const handleSubmit = async (query: string) => {
    const response = await fetch('/api/chat', {
      method: 'POST',
      body: JSON.stringify({
        query: query,
        user_id: user.id,
        document_filter: currentDocumentName,
      })
    });
  };

  return (
    <main className="w-full h-screen">
      <ChatInterface 
        authToken={token} 
        userName={user.firstName || user.username || user.emailAddresses[0]?.emailAddress || 'User'} 
      />
    </main>
  );
}
