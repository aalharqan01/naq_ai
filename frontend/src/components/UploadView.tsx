"use client";

import { useState, useRef } from "react";
import {
  Upload,
  FileText,
  Mic,
  Image,
  CheckCircle2,
  AlertCircle,
  Loader2,
  X,
  Sparkles,
} from "lucide-react";
import { uploadDocument } from "@/lib/api";

interface UploadViewProps {
  language: "en" | "ar";
}

export default function UploadView({ language }: UploadViewProps) {
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [titleAr, setTitleAr] = useState("");
  const [description, setDescription] = useState("");
  const [source, setSource] = useState("National Archives of Qatar");
  const [lang, setLang] = useState("ar");
  const [dateOriginal, setDateOriginal] = useState("");
  const [location, setLocation] = useState("");
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<{ success: boolean; message: string } | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const isAr = language === "ar";
  const dir = isAr ? "rtl" : "ltr";

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      setFile(droppedFile);
      if (!title) setTitle(droppedFile.name.replace(/\.[^/.]+$/, ""));
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      if (!title) setTitle(selectedFile.name.replace(/\.[^/.]+$/, ""));
    }
  };

  const handleUpload = async () => {
    if (!file || !title) return;

    setUploading(true);
    setResult(null);

    try {
      await uploadDocument(file, {
        title,
        title_ar: titleAr || undefined,
        description: description || undefined,
        source,
        language: lang,
        date_original: dateOriginal || undefined,
        location: location || undefined,
      });
      setResult({
        success: true,
        message: isAr
          ? "تم رفع الوثيقة بنجاح! جاري المعالجة..."
          : "Document uploaded successfully! Processing...",
      });
      setFile(null);
      setTitle("");
      setTitleAr("");
      setDescription("");
      setDateOriginal("");
      setLocation("");
    } catch (err) {
      setResult({
        success: false,
        message:
          err instanceof Error ? err.message : "Upload failed",
      });
    } finally {
      setUploading(false);
    }
  };

  const getFileIcon = () => {
    if (!file) return <Upload className="w-10 h-10" />;
    const ext = file.name.split(".").pop()?.toLowerCase();
    if (["mp3", "wav", "m4a", "ogg", "flac"].includes(ext || ""))
      return <Mic className="w-10 h-10" />;
    if (["pdf"].includes(ext || "")) return <FileText className="w-10 h-10" />;
    if (["png", "jpg", "jpeg", "tiff"].includes(ext || ""))
      return <Image className="w-10 h-10" />;
    return <FileText className="w-10 h-10" />;
  };

  return (
    <div className="max-w-2xl mx-auto px-6 py-8" dir={dir}>
      {/* Page title */}
      <div className="mb-8">
        <h2 className="text-2xl md:text-3xl font-display font-bold text-warm-white mb-2">
          {isAr ? "رفع وثيقة تراثية" : "Upload Heritage Document"}
        </h2>
        <p className="text-warm-dim text-sm">
          {isAr
            ? "ارفع وثائق أو تسجيلات صوتية ليتم معالجتها وفهرستها بالذكاء الاصطناعي"
            : "Upload documents or audio recordings to be AI-processed and indexed"}
        </p>
        <div className="gold-line max-w-xs mt-4" />
      </div>

      {/* Result notification */}
      {result && (
        <div
          className={`flex items-center gap-3 p-4 rounded-xl mb-6 ${
            result.success
              ? "bg-palm/10 text-palm border border-palm/20"
              : "bg-adaam/10 text-adaam-300 border border-adaam/20"
          }`}
        >
          {result.success ? (
            <CheckCircle2 className="w-5 h-5 shrink-0" />
          ) : (
            <AlertCircle className="w-5 h-5 shrink-0" />
          )}
          <span className="text-sm">{result.message}</span>
          <button
            onClick={() => setResult(null)}
            className="ms-auto p-1 hover:bg-white/10 rounded transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Drop zone */}
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`relative border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all duration-300 ${
          dragOver
            ? "border-gold bg-gold/5"
            : file
            ? "border-palm/40 bg-palm/5"
            : "border-white/10 hover:border-gold/40 hover:bg-white/[0.02]"
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          onChange={handleFileSelect}
          className="hidden"
          accept=".mp3,.wav,.m4a,.ogg,.flac,.pdf,.png,.jpg,.jpeg,.tiff,.tif,.txt,.md"
        />
        <div
          className={`mx-auto mb-4 ${
            file ? "text-palm" : "text-warm-dim"
          }`}
        >
          {getFileIcon()}
        </div>
        {file ? (
          <div>
            <p className="font-medium text-warm-white">{file.name}</p>
            <p className="text-sm text-warm-dim mt-1">
              {(file.size / 1024 / 1024).toFixed(2)} MB
            </p>
          </div>
        ) : (
          <div>
            <p className="font-medium text-warm-white">
              {isAr ? "اسحب الملف هنا أو انقر للاختيار" : "Drag file here or click to browse"}
            </p>
            <p className="text-sm text-warm-dim mt-2">
              MP3, WAV, PDF, PNG, JPG, TXT
            </p>
          </div>
        )}
        {/* Corner decorations */}
        <div className="absolute top-3 left-3 w-4 h-4 border-t-2 border-l-2 border-gold/20 rounded-tl-lg" />
        <div className="absolute top-3 right-3 w-4 h-4 border-t-2 border-r-2 border-gold/20 rounded-tr-lg" />
        <div className="absolute bottom-3 left-3 w-4 h-4 border-b-2 border-l-2 border-gold/20 rounded-bl-lg" />
        <div className="absolute bottom-3 right-3 w-4 h-4 border-b-2 border-r-2 border-gold/20 rounded-br-lg" />
      </div>

      {/* Metadata form */}
      <div className="mt-8 space-y-5">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-warm-muted mb-2">
              {isAr ? "العنوان (إنجليزي) *" : "Title (English) *"}
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full px-4 py-3 rounded-xl glass-input text-warm-white placeholder:text-warm-dim text-sm outline-none"
              placeholder="Document title"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-warm-muted mb-2">
              {isAr ? "العنوان (عربي)" : "Title (Arabic)"}
            </label>
            <input
              type="text"
              value={titleAr}
              onChange={(e) => setTitleAr(e.target.value)}
              className="w-full px-4 py-3 rounded-xl glass-input text-warm-white placeholder:text-warm-dim text-sm outline-none"
              dir="rtl"
              placeholder="عنوان الوثيقة"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-warm-muted mb-2">
            {isAr ? "الوصف" : "Description"}
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={3}
            className="w-full px-4 py-3 rounded-xl glass-input text-warm-white placeholder:text-warm-dim text-sm outline-none resize-none"
            dir="auto"
            placeholder={isAr ? "وصف الوثيقة..." : "Describe the document..."}
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-warm-muted mb-2">
              {isAr ? "المصدر" : "Source"}
            </label>
            <input
              type="text"
              value={source}
              onChange={(e) => setSource(e.target.value)}
              className="w-full px-4 py-3 rounded-xl glass-input text-warm-white placeholder:text-warm-dim text-sm outline-none"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-warm-muted mb-2">
              {isAr ? "اللغة" : "Language"}
            </label>
            <select
              value={lang}
              onChange={(e) => setLang(e.target.value)}
              className="w-full px-4 py-3 rounded-xl glass-input text-warm-white text-sm outline-none appearance-none cursor-pointer"
              style={{ backgroundImage: "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23A29475' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E\")", backgroundRepeat: "no-repeat", backgroundPosition: "right 16px center" }}
            >
              <option value="ar">{isAr ? "العربية" : "Arabic"}</option>
              <option value="en">{isAr ? "الإنجليزية" : "English"}</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-warm-muted mb-2">
              {isAr ? "التاريخ الأصلي" : "Original Date"}
            </label>
            <input
              type="text"
              value={dateOriginal}
              onChange={(e) => setDateOriginal(e.target.value)}
              className="w-full px-4 py-3 rounded-xl glass-input text-warm-white placeholder:text-warm-dim text-sm outline-none"
              placeholder={isAr ? "مثال: 1940" : "e.g., circa 1940s"}
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-warm-muted mb-2">
            {isAr ? "الموقع" : "Location"}
          </label>
          <input
            type="text"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            className="w-full px-4 py-3 rounded-xl glass-input text-warm-white placeholder:text-warm-dim text-sm outline-none"
            dir="auto"
            placeholder={isAr ? "الدوحة، قطر" : "Doha, Qatar"}
          />
        </div>

        <button
          onClick={handleUpload}
          disabled={!file || !title || uploading}
          className="w-full btn-primary py-3.5 rounded-xl font-medium flex items-center justify-center gap-2.5 text-[15px]"
        >
          {uploading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              {isAr ? "جاري الرفع..." : "Uploading..."}
            </>
          ) : (
            <>
              <Sparkles className="w-5 h-5" />
              {isAr ? "رفع ومعالجة بالذكاء الاصطناعي" : "Upload & AI Process"}
            </>
          )}
        </button>

        <p className="text-center text-[11px] text-warm-dim mt-2">
          {isAr
            ? "سيتم معالجة الوثيقة تلقائياً: استخراج النص، التعرف على الكيانات، والفهرسة"
            : "Document will be auto-processed: text extraction, entity recognition, and indexing"}
        </p>
      </div>
    </div>
  );
}
