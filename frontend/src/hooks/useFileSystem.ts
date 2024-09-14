import { fetchFileData } from '@/lib/api'
import { FileData } from '@/types/types'
import { useEffect, useState } from 'react'

export function useFileSystem() {
  const [fileSystem, setFileSystem] = useState<FileData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    fetchFileSystemData()
  }, [])

  const fetchFileSystemData = async () => {
    try {
      setLoading(true)
      const data = await fetchFileData()
      console.log('Fetched file system data:', data) // デバッグログ
      setFileSystem(data)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err : new Error('An unknown error occurred'))
    } finally {
      setLoading(false)
    }
  }

  const getFileContent = async (fileName: string): Promise<string> => {
    // 実装は変更なし
  }

  return { fileSystem, loading, error, getFileContent }
}