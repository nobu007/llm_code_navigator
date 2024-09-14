import { FileNode } from '@/types/types'
import React from 'react'

interface FileListProps {
  files: FileNode[] | undefined
  onFileSelect?: (fileName: string) => void
}

const FileList: React.FC<FileListProps> = ({ files, onFileSelect }) => {
  const renderFileTree = (nodes: FileNode[] | undefined) => {
    if (!nodes || nodes.length === 0) {
      return <div>No files found</div>
    }

    return (
      <ul>
        {nodes.map((node) => (
          <li key={node.id}>
            <span onClick={() => onFileSelect && onFileSelect(node.name)}>
              {node.type === 'file' ? '📄 ' : '📁 '}
              {node.name}
            </span>
            {node.type === 'directory' && node.children && renderFileTree(node.children)}
          </li>
        ))}
      </ul>
    )
  }

  return (
    <div>
      {renderFileTree(files)}
    </div>
  )
}

export default FileList