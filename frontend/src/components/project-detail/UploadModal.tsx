import React, { useState } from "react";
import { Upload, AlertCircle, Loader2 } from "lucide-react";
import { Modal } from "../common/Modal";
import { uploadProjectDocument } from "../../services/api";
import type { DocumentRecord } from "../../types";

interface UploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  projectId: string;
  onUploadSuccess: (newDoc: DocumentRecord) => void;
}

export const UploadModal: React.FC<UploadModalProps> = ({
  isOpen,
  onClose,
  projectId,
  onUploadSuccess,
}) => {
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      setFile(selected);
      if (!title) {
        setTitle(selected.name.replace(/\.[^/.]+$/, ""));
      }
      setError(null);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError("Please select a file to upload.");
      return;
    }

    setUploading(true);
    setError(null);

    try {
      const result = await uploadProjectDocument(projectId, file, title);
      onUploadSuccess(result);
      onClose();
    } catch (err: any) {
      setError(err.message || "Failed to upload document.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={`Upload Document — ${projectId}`}>
      <form onSubmit={handleUpload} className="space-y-4">
        {error && (
          <div className="flex items-start gap-2 rounded-lg border border-[var(--color-danger-border)] bg-[var(--color-danger-bg)] p-3 text-xs text-[var(--color-danger-text)]">
            <AlertCircle className="h-4 w-4 shrink-0 text-[var(--color-danger-icon)] mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        <div>
          <label className="block text-xs font-mono uppercase tracking-wider text-[var(--color-text-secondary)] mb-1.5">
            Document Title
          </label>
          <input
            type="text"
            required
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g., Environmental Clearance Certificate"
            className="w-full rounded-lg border border-[var(--input-border)] bg-[var(--input-bg)] px-3 py-2 text-xs text-[var(--input-text)] placeholder-[var(--input-placeholder)] focus:border-[var(--color-brand-primary)] focus:outline-none"
          />
        </div>

        <div>
          <label className="block text-xs font-mono uppercase tracking-wider text-[var(--color-text-secondary)] mb-1.5">
            Select File (Max 10MB: PDF, DOCX, XLSX, PNG, JPG)
          </label>
          <div className="rounded-xl border border-dashed border-[var(--color-border-strong)] bg-[var(--color-bg-surface-soft)] p-6 text-center hover:border-[var(--color-border-accent)] transition">
            <input
              type="file"
              id="file-upload"
              onChange={handleFileChange}
              accept=".pdf,.docx,.doc,.xlsx,.png,.jpg,.jpeg"
              className="hidden"
            />
            <label
              htmlFor="file-upload"
              className="flex flex-col items-center justify-center cursor-pointer"
            >
              <Upload className="h-8 w-8 text-[var(--color-brand-primary)] mb-2" />
              {file ? (
                <span className="text-xs font-mono text-[var(--color-text-accent)] font-bold">{file.name}</span>
              ) : (
                <>
                  <span className="text-xs font-medium text-[var(--color-text-primary)]">
                    Click to browse files or drag and drop
                  </span>
                  <span className="text-[11px] text-[var(--color-text-tertiary)] mt-1">
                    PDF, DOCX, XLSX, PNG, JPG
                  </span>
                </>
              )}
            </label>
          </div>
        </div>

        <div className="flex items-center justify-end gap-2 pt-3 border-t border-[var(--color-border-subtle)]">
          <button
            type="button"
            onClick={onClose}
            disabled={uploading}
            className="rounded-lg px-4 py-2 text-xs font-medium text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={uploading || !file}
            className="inline-flex items-center gap-2 rounded-lg bg-[var(--color-brand-primary)] px-4 py-2 text-xs font-semibold text-[var(--color-brand-contrast)] shadow-[var(--shadow-xs)] transition hover:bg-[var(--color-brand-primary-hover)] disabled:opacity-50"
          >
            {uploading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Uploading...</span>
              </>
            ) : (
              <span>Upload Document</span>
            )}
          </button>
        </div>
      </form>
    </Modal>
  );
};
