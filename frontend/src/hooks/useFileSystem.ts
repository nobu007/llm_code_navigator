import { useEffect, useState } from 'react'

interface File {
  id: string
  name: string
  type: 'file' | 'directory'
  path: string
}

interface Relationship {
  source: string
  target: string
}

interface FileSystem {
  files: File[]
  relationships: Relationship[]
}

interface FileContent {
  id: string
  name: string
  type: 'file'
  path: string
  content: string
  imports: { name: string; path: string }[]
}

export function useFileSystem() {
  const [fileSystem, setFileSystem] = useState<FileSystem | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    fetchFileSystem()
  }, [])

  const fetchFileSystem = async () => {
    try {
      // モックデータを使用（実際のAPIが実装されるまで）
      const mockData: FileSystem = {
        files: [
          { id: '1', name: 'file1.js', type: 'file', path: '/src/file1.js' },
          { id: '2', name: 'file2.js', type: 'file', path: '/src/file2.js' },
          { id: '3', name: 'components', type: 'directory', path: '/src/components' },
        ],
        relationships: [
          { source: '3', target: '1' },
          { source: '3', target: '2' },
        ],
      }
      setFileSystem(mockData)
      setLoading(false)
    } catch (err) {
      setError(err instanceof Error ? err : new Error('An unknown error occurred'))
      setLoading(false)
    }
  }

  const fetchFileContent = async (id: string): Promise<FileContent> => {
    // モックデータを返す（実際のAPIが実装されるまで）
    return {
      id,
      name: `file${id}.js`,
      type: 'file',
      path: `/src/file${id}.js`,
      content: '// This is a mock file content',
      imports: [],
    }
  }

  return { fileSystem, loading, error, fetchFileContent }
}