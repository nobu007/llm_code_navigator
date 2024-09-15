import { FileEdge, FileNode } from '@/types/types'
import dynamic from 'next/dynamic'
import React from 'react'

const DynamicSigmaContainer = dynamic(
  () => import('./DynamicSigmaContainer'),
  { ssr: false, loading: () => <div>Loading graph...</div> }
)

interface FileGraphProps {
  files: FileNode[]
  relationships: FileEdge[]
}

const FileGraph: React.FC<FileGraphProps> = ({ files, relationships }) => {
  console.log('FileGraph received:', { files, relationships })

  if (!files) {
    return <div>No file data available</div>
  }

  if (files.length === 0) {
    return <div>No files in the data</div>
  }

  return (
    <div style={{ width: '100%', height: '500px' }}>
      <DynamicSigmaContainer files={files} relationships={relationships} />
    </div>
  )
}

export default FileGraph