import { FileData, FileNode } from '@/types/types'
import React, { useEffect, useState } from 'react'
import { fetchFileData } from '../../lib/api'

const FileList: React.FC = () => {
  const [fileData, setFileData] = useState<FileData | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadFileData = async () => {
      try {
        const data = await fetchFileData()
        setFileData(data)
      } catch (err) {
        setError('Failed to load file data')
        console.error(err)
      }
    }

    loadFileData()
  }, [])

  const renderFileTree = (nodes: FileNode[] | undefined) => {
    if (!nodes || nodes.length === 0) {
      return <div>No files found</div>
    }

    return (
      <ul>
        {nodes.map((node) => (
          <li key={node.id}>
            {node.type === 'file' ? '📄 ' : '📁 '}
            {node.name}
            {node.type === 'directory' && node.children && renderFileTree(node.children)}
          </li>
        ))}
      </ul>
    )
  }

  if (error) {
    return <div>Error: {error}</div>
  }

  if (!fileData) {
    return <div>Loading...</div>
  }

  return (
    <div>
      <h2>File Structure</h2>
      {renderFileTree(fileData.files)}
    </div>
  )
}

export default FileList