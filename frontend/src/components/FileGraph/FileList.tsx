import { FileNode } from '@/types'
import React from 'react'

interface FileListProps {
  files: FileNode[]
  selectedFile: string | null
  onSelectFile: (fileName: string) => void
}

const FileList: React.FC<FileListProps> = ({ files, selectedFile, onSelectFile }) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-4">
      <h2 className="text-xl font-semibold mb-2">File List</h2>
      <ul className="space-y-1">
        {files.map((file) => (
          <li key={file.id}>
            <button
              className={`w-full text-left px-2 py-1 rounded ${
                selectedFile === file.id ? 'bg-blue-100 text-blue-700' : 'hover:bg-gray-100'
              }`}
              onClick={() => onSelectFile(file.id)}
            >
              {file.label}
            </button>
          </li>
        ))}
      </ul>
    </div>
  )
}

export default FileList