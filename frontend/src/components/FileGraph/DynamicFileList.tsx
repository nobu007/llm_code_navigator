import { FileData, FileNode } from '@/types/types'
import dynamic from 'next/dynamic'
import React from 'react'

const DynamicFileList = dynamic(() => import('./FileList'), {
  ssr: false,
  loading: () => <p>Loading file list...</p>
})

interface DynamicFileListProps {
  files: FileData
  onFileSelect: (file: FileNode) => void
}

const FileListWrapper: React.FC<DynamicFileListProps> = ({ files, onFileSelect }) => {
  return <DynamicFileList files={files.files} onFileSelect={onFileSelect} />
}

export default FileListWrapper