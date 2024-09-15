import { FileEdge, FileNode } from '@/types/types'
import React from 'react'
import DynamicSigmaContainer from './DynamicSigmaContainer'
import LoadGraph from './LoadGraph'

interface FileGraphProps {
  files: FileNode[]
  relationships: FileEdge[]
}

const FileGraph: React.FC<FileGraphProps> = ({ files, relationships }) => {
  return (
    <DynamicSigmaContainer files={files} relationships={relationships}>
      <LoadGraph files={files} relationships={relationships} />
    </DynamicSigmaContainer>
  )
}

export default FileGraph