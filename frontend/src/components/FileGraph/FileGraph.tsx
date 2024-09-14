import { FileNode, Relationship } from '@/types/types'
import dynamic from 'next/dynamic'
import React from 'react'

const DynamicSigmaContainer = dynamic(
  () => import('./DynamicSigmaContainer'),
  { ssr: false }
)

interface FileGraphProps {
  files: FileNode[] | undefined
  relationships: Relationship[] | undefined
}

const FileGraph: React.FC<FileGraphProps> = ({ files, relationships }) => {
  console.log('FileGraph received:', { files, relationships }) // デバッグログ

  if (!files || !relationships) {
    return <div>Loading graph data...</div>
  }

  return (
    <div className="w-full h-[500px]">
      <DynamicSigmaContainer files={files} relationships={relationships} />
    </div>
  )
}

export default FileGraph