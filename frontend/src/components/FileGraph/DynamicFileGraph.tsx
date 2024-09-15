import { FileData, FileEdge, FileNode } from '@/types/types'
import dynamic from 'next/dynamic'
import React from 'react'

const DynamicSigmaContainer = dynamic(() => import('./DynamicSigmaContainer'), {
  ssr: false,
  loading: () => <p>Loading graph...</p>
})

interface DynamicFileGraphProps {
  fileData: FileData | null
}

const DynamicFileGraph: React.FC<DynamicFileGraphProps> = ({ fileData }) => {
  if (!fileData) {
    return <p>No file data available</p>
  }

  const files: FileNode[] = fileData.files

  const relationships: FileEdge[] =fileData.relationships

  return <DynamicSigmaContainer files={files} relationships={relationships} />
}

export default DynamicFileGraph