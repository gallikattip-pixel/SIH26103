import React, { useState } from "react";
import { FileText, Download, Trash2, Plus, FileCheck } from "lucide-react";
import type { DocumentRecord } from "../../types";
import { UploadModal } from "./UploadModal";
import { deleteProjectDocument } from "../../services/api";

interface DocumentsTabProps {
  projectId: string;
  initialDocuments: DocumentRecord[];
}

export const DocumentsTab: React.FC<DocumentsTabProps> = ({ projectId, initialDocuments }) => {
  const [documents, setDocuments] = useState<DocumentRecord[]>(initialDocuments);
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const handleUploadSuccess = (newDoc: DocumentRecord) => {
    setDocuments([newDoc, ...documents]);
  };

  const handleDelete = async (docId: string) => {
    if (!window.confirm("Are you sure you want to remove this document reference?")) return;
    setDeletingId(docId);
    try {
      await deleteProjectDocument(projectId, docId);
      setDocuments(documents.filter((d) => d.id !== docId));
    } catch {
      alert("Failed to delete document reference.");
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="space-y-4">
      {/* Header and Upload Trigger */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-[var(--color-border-subtle)] pb-3">
        <div>
          <h4 className="text-sm font-semibold text-[var(--color-text-primary)] uppercase tracking-wider font-mono">
            Project Clearances & Documents
          </h4>
          <p className="text-xs text-[var(--color-text-tertiary)]">
            Stored in Cloud Storage with metadata tracked in Firebase Realtime Database
          </p>
        </div>
        <button
          onClick={() => setIsUploadOpen(true)}
          className="inline-flex items-center gap-1.5 rounded-lg bg-[var(--color-brand-primary)] px-3 py-1.5 text-xs font-semibold text-[var(--color-brand-contrast)] shadow-[var(--shadow-xs)] transition hover:bg-[var(--color-brand-primary-hover)]"
        >
          <Plus className="h-4 w-4" />
          <span>Upload Document</span>
        </button>
      </div>

      {/* Documents List or Professional Empty State */}
      {documents.length === 0 ? (
        <div className="rounded-xl border border-dashed border-[var(--color-border-strong)] bg-[var(--color-bg-surface)] p-8 text-center">
          <FileText className="mx-auto h-8 w-8 text-[var(--color-text-muted)] mb-2" />
          <p className="text-xs font-semibold text-[var(--color-text-primary)]">
            No project documents are currently available.
          </p>
          <p className="text-[11px] text-[var(--color-text-tertiary)] mt-1 max-w-sm mx-auto">
            Upload blueprints, technical audit logs, environmental clearances, or financial sanction letters.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {documents.map((doc) => (
            <div
              key={doc.id}
              className="flex items-center justify-between rounded-xl border border-[var(--document-border)] bg-[var(--document-bg)] p-4 transition hover:border-[var(--document-border-hover)] hover:bg-[var(--document-bg-hover)] shadow-[var(--shadow-xs)]"
            >
              <div className="flex items-start gap-3 min-w-0">
                <div className="rounded-lg border border-[var(--color-border-accent)] bg-[var(--document-icon-bg)] p-2 text-[var(--document-icon)] shrink-0">
                  <FileCheck className="h-4 w-4" />
                </div>
                <div className="min-w-0">
                  <p className="text-xs font-semibold text-[var(--color-text-primary)] truncate">{doc.title}</p>
                  <p className="text-[11px] text-[var(--color-text-secondary)] truncate font-mono mt-0.5">
                    {doc.filename} • {doc.file_size_kb} KB
                  </p>
                  <p className="text-[10px] text-[var(--color-text-tertiary)] font-mono">
                    Uploaded: {new Date(doc.uploaded_at).toLocaleDateString()}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-1.5 shrink-0 ml-3">
                <a
                  href={doc.download_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="rounded-lg border border-[var(--color-border-strong)] bg-[var(--color-bg-surface)] p-2 text-[var(--color-text-secondary)] transition hover:bg-[var(--color-bg-surface-muted)] hover:text-[var(--color-text-primary)]"
                  title="Download / View"
                >
                  <Download className="h-3.5 w-3.5" />
                </a>
                <button
                  onClick={() => handleDelete(doc.id)}
                  disabled={deletingId === doc.id}
                  className="rounded-lg border border-[var(--color-danger-border)] bg-[var(--color-danger-bg)] p-2 text-[var(--color-danger-text)] transition hover:bg-[var(--color-danger-border)]/50"
                  title="Delete"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Upload Modal */}
      <UploadModal
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
        projectId={projectId}
        onUploadSuccess={handleUploadSuccess}
      />
    </div>
  );
};
