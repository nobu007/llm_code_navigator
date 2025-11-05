import { FileEdge, FileNode } from '@/types/types'
import React from 'react'
import DynamicSigmaContainer from './DynamicSigmaContainer'
import LoadGraph from './LoadGraph'

interface FileGraphProps {
  files: FileNode[]
  relationships: FileEdge[]
  onNodeClick?: (file: FileNode, event: MouseEvent) => void
}

const FileGraph: React.FC<FileGraphProps> = ({ files, relationships, onNodeClick }) => {
  const handleNodeClick = (file: FileNode, event: MouseEvent) => {
    if (onNodeClick) {
      onNodeClick(file, event)
    }
  }

  return (
    <DynamicSigmaContainer files={files} relationships={relationships}>
      <LoadGraph files={files} relationships={relationships} onNodeClick={handleNodeClick} />
    </DynamicSigmaContainer>
  )
}

export default FileGraph