"use client";

import { useState, useEffect } from "react";
import {
  FileText,
  Mic,
  Image,
  File,
  Clock,
  CheckCircle2,
  AlertCircle,
  Loader2,
  MapPin,
  Calendar,
  Tag,
  Database,
  Layers,
  Headphones,
} from "lucide-react";
import { getDocuments, getStats, type Document, type ArchiveStats } from "@/lib/api";
import { formatDate, detectDirection } from "@/lib/utils";

interface ArchiveViewProps {
  language: "en" | "ar";
}

const typeIcons: Record<string, React.ReactNode> = {
  audio: <Mic className="w-5 h-5" />,
  pdf: <FileText className="w-5 h-5" />,
  image: <Image className="w-5 h-5" />,
  text: <File className="w-5 h-5" />,
};

const statusConfig: Record<string, { icon: React.ReactNode; className: string; label: string; labelAr: string }> = {
  completed: {
    icon: <CheckCircle2 className="w-3.5 h-3.5" />,
    className: "text-palm bg-palm/10 border border-palm/20",
    label: "Processed",
    labelAr: "مكتمل",
  },
  processing: {
    icon: <Loader2 className="w-3.5 h-3.5 animate-spin" />,
    className: "text-sea bg-sea/10 border border-sea/20",
    label: "Processing",
    labelAr: "قيد المعالجة",
  },
  pending: {
    icon: <Clock className="w-3.5 h-3.5" />,
    className: "text-gold-muted bg-gold/10 border border-gold/20",
    label: "Pending",
    labelAr: "قيد الانتظار",
  },
  failed: {
    icon: <AlertCircle className="w-3.5 h-3.5" />,
    className: "text-adaam-300 bg-adaam/10 border border-adaam/20",
    label: "Failed",
    labelAr: "فشل",
  },
};

export default function ArchiveView({ language }: ArchiveViewProps) {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [stats, setStats] = useState<ArchiveStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedDoc, setSelectedDoc] = useState<Document | null>(null);

  const isAr = language === "ar";
  const dir = isAr ? "rtl" : "ltr";

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [docsRes, statsRes] = await Promise.all([
        getDocuments(),
        getStats(),
      ]);
      setDocuments(docsRes.documents);
      setStats(statsRes);
    } catch (err) {
      console.error("Failed to load archive data:", err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="w-8 h-8 animate-spin text-gold" />
          <span className="text-warm-dim text-sm">
            {isAr ? "جاري تحميل الأرشيف..." : "Loading archive..."}
          </span>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-6 py-8" dir={dir}>
      {/* Page title */}
      <div className="mb-8">
        <h2 className="text-2xl md:text-3xl font-display font-bold text-warm-white mb-2">
          {isAr ? "الأرشيف الرقمي" : "Digital Archive"}
        </h2>
        <p className="text-warm-dim text-sm">
          {isAr
            ? "استعرض الوثائق والتسجيلات المعالجة بالذكاء الاصطناعي"
            : "Browse AI-processed documents and recordings"}
        </p>
        <div className="gold-line max-w-xs mt-4" />
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
          <div className="stat-card group">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-2.5 rounded-xl bg-adaam/15 text-adaam-300 border border-adaam/20 group-hover:bg-adaam/25 transition-colors">
                <FileText className="w-5 h-5" />
              </div>
            </div>
            <p className="text-3xl font-bold text-warm-white font-display">
              {stats.total_documents}
            </p>
            <p className="text-xs text-warm-dim mt-1 uppercase tracking-wider">
              {isAr ? "وثيقة" : "Documents"}
            </p>
          </div>

          <div className="stat-card group">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-2.5 rounded-xl bg-gold/10 text-gold border border-gold/20 group-hover:bg-gold/20 transition-colors">
                <Database className="w-5 h-5" />
              </div>
            </div>
            <p className="text-3xl font-bold text-warm-white font-display">
              {stats.vectors_count}
            </p>
            <p className="text-xs text-warm-dim mt-1 uppercase tracking-wider">
              {isAr ? "متجه مفهرس" : "Indexed Vectors"}
            </p>
          </div>

          <div className="stat-card group">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-2.5 rounded-xl bg-palm/10 text-palm border border-palm/20 group-hover:bg-palm/20 transition-colors">
                <Layers className="w-5 h-5" />
              </div>
            </div>
            <p className="text-3xl font-bold text-warm-white font-display">
              {stats.completed}
            </p>
            <p className="text-xs text-warm-dim mt-1 uppercase tracking-wider">
              {isAr ? "مكتمل" : "Processed"}
            </p>
          </div>

          <div className="stat-card group">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-2.5 rounded-xl bg-sea/10 text-sea border border-sea/20 group-hover:bg-sea/20 transition-colors">
                <Headphones className="w-5 h-5" />
              </div>
            </div>
            <p className="text-3xl font-bold text-warm-white font-display">
              {stats.by_type.audio || 0}
            </p>
            <p className="text-xs text-warm-dim mt-1 uppercase tracking-wider">
              {isAr ? "تسجيل صوتي" : "Audio Records"}
            </p>
          </div>
        </div>
      )}

      {/* Document grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {documents.map((doc) => {
          const status = statusConfig[doc.status] || statusConfig.pending;
          const entities = doc.entities_json
            ? JSON.parse(doc.entities_json)
            : [];

          return (
            <div
              key={doc.id}
              onClick={() => setSelectedDoc(selectedDoc?.id === doc.id ? null : doc)}
              className={`doc-card ${
                selectedDoc?.id === doc.id ? "selected" : ""
              }`}
            >
              {/* Header */}
              <div className="flex items-start gap-3 mb-3">
                <div className="p-2.5 rounded-xl bg-adaam/15 text-adaam-300 border border-adaam/20 shrink-0">
                  {typeIcons[doc.doc_type] || <File className="w-5 h-5" />}
                </div>
                <div className="flex-1 min-w-0">
                  <h3
                    className="font-semibold text-warm-white truncate text-[15px]"
                    dir={detectDirection(doc.title)}
                  >
                    {isAr && doc.title_ar ? doc.title_ar : doc.title}
                  </h3>
                  <p className="text-[11px] text-warm-dim mt-0.5 uppercase tracking-wider">
                    {doc.source || "National Archives of Qatar"}
                  </p>
                </div>
                <span
                  className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-medium shrink-0 ${status.className}`}
                >
                  {status.icon}
                  <span className="hidden sm:inline">
                    {isAr ? status.labelAr : status.label}
                  </span>
                </span>
              </div>

              {/* Description */}
              {(doc.description || doc.description_ar) && (
                <p
                  className="text-sm text-warm-muted mb-3 line-clamp-2 leading-relaxed"
                  dir={detectDirection(
                    (isAr ? doc.description_ar : doc.description) || ""
                  )}
                >
                  {isAr && doc.description_ar
                    ? doc.description_ar
                    : doc.description}
                </p>
              )}

              {/* Metadata chips */}
              <div className="flex flex-wrap gap-1.5">
                {doc.date_original && (
                  <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-white/5 text-[11px] text-warm-dim border border-white/5">
                    <Calendar className="w-3 h-3 text-gold-muted" />
                    {doc.date_original}
                  </span>
                )}
                {doc.location && (
                  <span
                    className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-white/5 text-[11px] text-warm-dim border border-white/5"
                    dir={detectDirection(doc.location)}
                  >
                    <MapPin className="w-3 h-3 text-gold-muted" />
                    {doc.location}
                  </span>
                )}
                {doc.language && (
                  <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-white/5 text-[11px] text-warm-dim border border-white/5">
                    {doc.language === "ar" ? "العربية" : "English"}
                  </span>
                )}
              </div>

              {/* Expanded detail */}
              {selectedDoc?.id === doc.id && (
                <div className="mt-4 pt-4 border-t border-white/5">
                  {/* Entities */}
                  {entities.length > 0 && (
                    <div className="mb-4">
                      <p className="text-[11px] font-medium text-warm-dim mb-2 uppercase tracking-wider">
                        {isAr ? "الكيانات المستخرجة" : "Extracted Entities"}
                      </p>
                      <div className="flex flex-wrap gap-1.5">
                        {entities.slice(0, 10).map(
                          (e: { text: string; label: string }, i: number) => (
                            <span
                              key={i}
                              className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] bg-adaam/10 text-adaam-300 border border-adaam/20"
                            >
                              <Tag className="w-3 h-3" />
                              {e.text}
                              <span className="text-adaam-400 opacity-60">
                                {e.label}
                              </span>
                            </span>
                          )
                        )}
                      </div>
                    </div>
                  )}

                  {/* Preview text */}
                  {doc.processed_text && (
                    <div>
                      <p className="text-[11px] font-medium text-warm-dim mb-2 uppercase tracking-wider">
                        {isAr ? "معاينة المحتوى" : "Content Preview"}
                      </p>
                      <p
                        className="text-xs text-warm-muted line-clamp-4 leading-relaxed"
                        dir={detectDirection(doc.processed_text)}
                      >
                        {doc.processed_text.slice(0, 300)}...
                      </p>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Empty state */}
      {documents.length === 0 && (
        <div className="text-center py-20">
          <div className="relative w-20 h-20 mx-auto mb-6">
            <div className="absolute inset-0 rounded-full bg-white/5 border border-white/10" />
            <div className="absolute inset-0 flex items-center justify-center">
              <FileText className="w-8 h-8 text-warm-dim" />
            </div>
          </div>
          <p className="text-warm-muted text-lg font-display">
            {isAr ? "لا توجد وثائق بعد" : "No documents yet"}
          </p>
          <p className="text-sm text-warm-dim mt-2 max-w-sm mx-auto">
            {isAr
              ? "قم برفع الوثائق أو تشغيل بيانات العرض التجريبي"
              : "Upload documents or run the demo seed script to get started"}
          </p>
        </div>
      )}
    </div>
  );
}
