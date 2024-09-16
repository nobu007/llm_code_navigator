import { FileData, FileNode } from '@/types/types'
import dynamic from 'next/dynamic'
import React, { useState } from 'react'

const DynamicFileList = dynamic(() => import('@/components/FileGraph/DynamicFileList'), {
  ssr: false,
  loading: () => <p>Loading file list...</p>
})

const DynamicFileGraph = dynamic(() => import('@/components/FileGraph/DynamicFileGraph'), {
  ssr: false,
  loading: () => <p>Loading file graph...</p>
})

const DynamicFileContent = dynamic(() => import('@/components/FileGraph/DynamicFileContent'), {
  ssr: false,
  loading: () => <p>Loading file content...</p>
})

interface LayoutProps {
  fileSystem: FileData
  getFileContent: (path: string) => Promise<string>
}

const Layout: React.FC<LayoutProps> = ({ fileSystem, getFileContent }) => {
  const [selectedFile, setSelectedFile] = useState<FileNode | null>(null)
  const [fileContent, setFileContent] = useState<string | null>(null)

  const handleFileSelect = async (file: FileNode) => {
    setSelectedFile(file)
    try {
      const content = await getFileContent(file.name)
      setFileContent(content)
    } catch (error) {
      console.error('Error fetching file content:', error)
      setFileContent('Error loading file content')
    }
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">LLM Code Navigator</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <DynamicFileList files={fileSystem.files} onFileSelect={handleFileSelect} />
        </div>
        <div>
          <DynamicFileGraph fileData={fileSystem} />
        </div>
      </div>
      <div className="mt-6">
        <DynamicFileContent fileName={selectedFile?.name || null} content={fileContent} />
      </div>
    </div>
  )
}

export default Layout