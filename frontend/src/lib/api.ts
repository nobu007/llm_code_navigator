import { FileData } from '@/types'

const API_URL = 'http://localhost:9000'

export const fetchFileData = async (): Promise<FileData> => {
  const response = await fetch(`${API_URL}/api/files/files_info`)
  if (!response.ok) {
    throw new Error('Failed to fetch file data')
  }
  return response.json()
}

export const fetchFileContent = async (fileName: string): Promise<string> => {
  const response = await fetch(`${API_URL}/api/files/file_content/${fileName}`)
  if (!response.ok) {
    throw new Error('Failed to fetch file content')
  }
  const data = await response.json()
  return data.content
}