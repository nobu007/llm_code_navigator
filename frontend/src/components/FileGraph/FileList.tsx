import { FileNode } from '@/types/types'
import React from 'react'

interface FileListProps {
  files: FileNode[]
  onFileSelect: (file: FileNode) => void
}

const FileList: React.FC<FileListProps> = ({ files, onFileSelect }) => {
  const renderFileTree = (nodes: FileNode[]) => {
    return (
      <ul className="space-y-1">
        {nodes.map((node) => (
          <li key={node.id}>
            <button
              onClick={() => onFileSelect(node)}
              className="w-full text-left px-2 py-1 hover:bg-gray-100 rounded flex items-center"
            >
              {node.type === 'directory' ? (
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                </svg>
              ) : (
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              )}
              {node.name}
            </button>
            {node.children && node.children.length > 0 && (
              <div className="ml-4 mt-1">
                {renderFileTree(node.children)}
              </div>
            )}
          </li>
        ))}
      </ul>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-4">
      <h2 className="text-xl font-semibold mb-2">Files</h2>
      {renderFileTree(files)}
    </div>
  )
}

export default FileList