import { FileNode } from '@/types/types'
import dynamic from 'next/dynamic'
import React from 'react'

const FileList = dynamic(() => import('./FileList'), {
  ssr: false,
  loading: () => <p>Loading file list...</p>
})

interface DynamicFileListProps {
  files: FileNode[]
  onFileSelect: (file: FileNode) => void
}

const DynamicFileList: React.FC<DynamicFileListProps> = ({ files, onFileSelect }) => {
  return <FileList files={files} onFileSelect={onFileSelect} />
}

export default DynamicFileList