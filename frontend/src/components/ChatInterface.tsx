"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Loader2, BookOpen, ChevronDown, ChevronUp } from "lucide-react";
import { askQuestion, type SourceReference } from "@/lib/api";
import { detectDirection } from "@/lib/utils";

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: SourceReference[];
}

interface ChatInterfaceProps {
  language: "en" | "ar";
}

const SUGGESTED_QUESTIONS = {
  en: [
    "What was pearl diving like in Qatar?",
    "Tell me about Al Zubarah",
    "Role of women in traditional Qatar",
    "How did Doha transform?",
    "Traditional Qatari architecture",
  ],
  ar: [
    "كيف كان الغوص على اللؤلؤ في قطر؟",
    "أخبرني عن موقع الزبارة الأثري",
    "ما دور المرأة في المجتمع القطري؟",
    "كيف تحولت الدوحة؟",
    "العمارة القطرية التقليدية",
  ],
};

export default function ChatInterface({ language }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string>();
  const [expandedSources, setExpandedSources] = useState<Set<number>>(new Set());
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const isAr = language === "ar";
  const dir = isAr ? "rtl" : "ltr";

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = async (question?: string) => {
    const q = question || input.trim();
    if (!q || loading) return;
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: q }]);
    setLoading(true);
    try {
      const response = await askQuestion(q, sessionId, language);
      setSessionId(response.session_id);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: response.answer, sources: response.sources },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: isAr
            ? "عذرا، حدث خطأ. يرجى المحاولة مرة أخرى."
            : "Sorry, an error occurred. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSubmit(); }
  };

  const toggleSource = (idx: number) => {
    setExpandedSources((prev) => {
      const next = new Set(prev);
      next.has(idx) ? next.delete(idx) : next.add(idx);
      return next;
    });
  };

  return (
    <div className="flex flex-col h-[calc(100vh-64px)]" dir={dir}>
      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-8">
        <div className="max-w-3xl mx-auto space-y-6">
          {/* Welcome */}
          {messages.length === 0 && (
            <div className="text-center py-12">
              {/* Geometric hero emblem */}
              <div className="relative w-28 h-28 mx-auto mb-8">
                <div className="absolute inset-0 rounded-full bg-adaam/10 animate-glow-pulse" />
                <div className="absolute inset-2 rounded-full border border-gold/20" />
                <div className="absolute inset-4 rounded-full border border-adaam/30" />
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-shimmer font-display text-4xl font-bold">
                    {isAr ? "ذ" : "D"}
                  </span>
                </div>
              </div>

              <h2 className="text-3xl md:text-4xl font-display font-bold text-warm-white mb-3">
                {isAr ? "مرحبا بك في ذاكرة" : "Welcome to Dhakira"}
              </h2>
              <p className="text-warm-muted mb-2 max-w-lg mx-auto leading-relaxed">
                {isAr
                  ? "مساعد الذكاء الاصطناعي للأرشيف الوطني لدولة قطر"
                  : "AI Heritage Assistant for the National Archives of Qatar"}
              </p>
              <p className="text-warm-dim text-sm mb-10 max-w-md mx-auto">
                {isAr
                  ? "اسأل عن تراث قطر واستكشف التاريخ من خلال الوثائق المؤرشفة"
                  : "Ask about Qatar's heritage and explore history through archived documents"}
              </p>

              <div className="gold-line max-w-xs mx-auto mb-10" />

              {/* Suggested questions */}
              <div className="flex flex-wrap justify-center gap-3 max-w-2xl mx-auto">
                {SUGGESTED_QUESTIONS[language].map((q, i) => (
                  <button
                    key={i}
                    onClick={() => handleSubmit(q)}
                    className="btn-ghost px-5 py-2.5 text-sm font-arabic"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Messages */}
          {messages.map((msg, i) => (
            <div key={i}>
              <div className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                <div
                  className={`max-w-[85%] ${msg.role === "user" ? "chat-user" : "chat-assistant"}`}
                  dir={detectDirection(msg.content)}
                >
                  <p className="whitespace-pre-wrap leading-relaxed text-[15px]">{msg.content}</p>
                </div>
              </div>

              {/* Sources */}
              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-3 ms-2">
                  <button
                    onClick={() => toggleSource(i)}
                    className="flex items-center gap-2 text-xs text-gold-muted hover:text-gold transition-colors group"
                  >
                    <BookOpen className="w-3.5 h-3.5" />
                    <span>
                      {isAr
                        ? `${msg.sources.length} مصادر أرشيفية`
                        : `${msg.sources.length} archival sources`}
                    </span>
                    {expandedSources.has(i) ? (
                      <ChevronUp className="w-3 h-3 transition-transform" />
                    ) : (
                      <ChevronDown className="w-3 h-3 transition-transform" />
                    )}
                  </button>

                  {expandedSources.has(i) && (
                    <div className="mt-3 space-y-2">
                      {msg.sources.map((src, si) => (
                        <div key={si} className="source-card">
                          <div className="flex items-start justify-between gap-3">
                            <span className="font-medium text-gold text-sm">{src.document_title}</span>
                            <span className="text-[10px] px-2 py-0.5 rounded-full bg-adaam/20 text-adaam-300 shrink-0 border border-adaam/20">
                              {Math.round(src.relevance_score * 100)}%
                            </span>
                          </div>
                          <p
                            className="mt-2 text-warm-dim text-xs leading-relaxed"
                            dir={detectDirection(src.chunk_text)}
                          >
                            {src.chunk_text}
                          </p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}

          {/* Typing indicator */}
          {loading && (
            <div className="flex justify-start">
              <div className="chat-assistant flex items-center gap-2 py-4 px-6">
                {[0, 1, 2].map((i) => (
                  <div
                    key={i}
                    className="w-2 h-2 rounded-full bg-gold/60 animate-typing-bounce"
                    style={{ animationDelay: `${i * 0.2}s` }}
                  />
                ))}
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input */}
      <div className="border-t border-white/5 px-4 py-4" style={{
        background: "rgba(10, 10, 15, 0.8)",
        backdropFilter: "blur(20px)",
      }}>
        <div className="max-w-3xl mx-auto">
          <div className="flex items-end gap-3 glass-input rounded-2xl px-5 py-3">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={isAr ? "اسأل عن تراث قطر..." : "Ask about Qatar's heritage..."}
              className="flex-1 resize-none bg-transparent outline-none text-warm-white placeholder:text-warm-dim max-h-32 text-[15px] font-arabic"
              rows={1}
              dir="auto"
            />
            <button
              onClick={() => handleSubmit()}
              disabled={!input.trim() || loading}
              className="btn-primary p-2.5 rounded-xl shrink-0"
            >
              {loading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </button>
          </div>
          <p className="text-center text-[11px] text-warm-dim mt-3 font-arabic">
            {isAr
              ? "ذاكرة تعتمد على الوثائق المؤرشفة من الأرشيف الوطني لدولة قطر"
              : "Dhakira draws from archived documents of the National Archives of Qatar"}
          </p>
        </div>
      </div>
    </div>
  );
}
