import dynamic from 'next/dynamic'
import React from 'react'
import { useFileSystem } from '../../hooks/useFileSystem'

const DynamicFileGraph = dynamic(() => import('./DynamicFileGraph'), {
  ssr: false,
})

const FileGraph: React.FC = () => {
  const { fileSystem, loading, error } = useFileSystem()

  if (loading) return <div>Loading...</div>
  if (error) return <div>Error: {error.message}</div>

  return <DynamicFileGraph fileSystem={fileSystem} />
}

export default FileGraph