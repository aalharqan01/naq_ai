"use client";

import { useState } from "react";
import Header from "@/components/Header";
import ChatInterface from "@/components/ChatInterface";
import ArchiveView from "@/components/ArchiveView";
import UploadView from "@/components/UploadView";

export default function Home() {
  const [language, setLanguage] = useState<"en" | "ar">("en");
  const [activeTab, setActiveTab] = useState("chat");

  const toggleLanguage = () => {
    setLanguage((prev) => (prev === "en" ? "ar" : "en"));
  };

  return (
    <div className="min-h-screen flex flex-col" dir={language === "ar" ? "rtl" : "ltr"}>
      <Header
        language={language}
        onLanguageToggle={toggleLanguage}
        activeTab={activeTab}
        onTabChange={setActiveTab}
      />
      <main className="flex-1">
        {activeTab === "chat" && <ChatInterface language={language} />}
        {activeTab === "archive" && <ArchiveView language={language} />}
        {activeTab === "upload" && <UploadView language={language} />}
      </main>
    </div>
  );
}
