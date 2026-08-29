import { useDropzone } from 'react-dropzone'
import { Upload, AlertCircle } from 'lucide-react'
import { cn } from '../lib/cn'

// Accepted MIME types and their display extensions
// react-dropzone v14 format: { 'mime/type': ['.ext', ...] }
const ACCEPTED_TYPES = {
  'application/pdf': ['.pdf'],
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
  'audio/mpeg':  ['.mp3'],
  'audio/wav':   ['.wav'],
  'image/jpeg':  ['.jpg', '.jpeg'],
  'image/png':   ['.png'],
}

const MAX_SIZE_BYTES = 100 * 1024 * 1024 // 100 MB

/** Human-readable rejection reason from react-dropzone error code */
function getRejectionReason(code, file) {
  if (code === 'file-too-large') {
    const mb = (file.size / (1024 * 1024)).toFixed(1)
    return `${file.name} is too large (${mb} MB — max 100 MB)`
  }
  if (code === 'file-invalid-type') {
    return `${file.name} — unsupported type. Accepted: PDF, DOCX, MP3, WAV, JPG, PNG`
  }
  return `${file.name} was rejected`
}

/**
 * Drag-and-drop / click-to-browse file picker.
 *
 * @param {{ onAccept: (files: File[]) => void }} props
 */
export default function UploadDropzone({ onAccept }) {
  const {
    getRootProps,
    getInputProps,
    isDragActive,
    isDragReject,
    fileRejections,
  } = useDropzone({
    accept:   ACCEPTED_TYPES,
    maxSize:  MAX_SIZE_BYTES,
    multiple: true,
    onDropAccepted: onAccept,
  })

  const hasRejections = fileRejections.length > 0

  return (
    <div className="flex flex-col gap-3">
      {/* ── Drop zone ── */}
      <div
        {...getRootProps()}
        id="aqila-dropzone"
        className={cn(
          'flex flex-col items-center justify-center gap-3 px-6 py-10',
          'rounded-xl border-2 border-dashed cursor-pointer',
          'transition-all duration-200 outline-none',
        )}
        style={{
          borderColor: isDragReject
            ? 'rgba(239,68,68,0.5)'
            : isDragActive
            ? 'rgba(29,158,117,0.7)'
            : 'rgba(29,158,117,0.28)',
          background: isDragReject
            ? 'rgba(239,68,68,0.05)'
            : isDragActive
            ? 'rgba(29,158,117,0.10)'
            : 'rgba(29,158,117,0.04)',
        }}
      >
        <input {...getInputProps()} id="aqila-file-input" />

        {/* Upload icon */}
        <div
          className="flex items-center justify-center w-12 h-12 rounded-xl transition-transform duration-200"
          style={{
            background: isDragActive
              ? 'rgba(29,158,117,0.25)'
              : 'rgba(29,158,117,0.12)',
            transform: isDragActive ? 'scale(1.1)' : 'scale(1)',
          }}
        >
          <Upload
            size={22}
            style={{
              color: isDragReject ? '#ef4444' : 'var(--accent-teal)',
            }}
          />
        </div>

        {/* Text */}
        <div className="text-center select-none">
          {isDragReject ? (
            <p className="text-sm font-medium" style={{ color: '#ef4444' }}>
              Some files are not supported
            </p>
          ) : isDragActive ? (
            <p className="text-sm font-medium" style={{ color: '#43ce9e' }}>
              Release to add files
            </p>
          ) : (
            <>
              <p className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>
                Drop files here, or{' '}
                <span style={{ color: '#43ce9e' }}>click to browse</span>
              </p>
              <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>
                PDF · DOCX · MP3 · WAV · JPG · PNG &nbsp;—&nbsp; up to 100 MB each
              </p>
            </>
          )}
        </div>
      </div>

      {/* ── Rejection messages ── */}
      {hasRejections && (
        <div
          className="flex flex-col gap-1.5 px-4 py-3 rounded-lg"
          style={{
            background:  'rgba(239,68,68,0.08)',
            border:      '1px solid rgba(239,68,68,0.2)',
          }}
        >
          {fileRejections.map(({ file, errors }) =>
            errors.map((err) => (
              <div key={`${file.name}-${err.code}`} className="flex items-start gap-2">
                <AlertCircle
                  size={14}
                  className="shrink-0 mt-0.5"
                  style={{ color: '#ef4444' }}
                />
                <p className="text-xs" style={{ color: '#fca5a5' }}>
                  {getRejectionReason(err.code, file)}
                </p>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  )
}
