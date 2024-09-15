import dynamic from 'next/dynamic'
import React from 'react'

const FileContent = dynamic(() => import('./FileContent'), {
  ssr: false,
  loading: () => <p>Loading file content...</p>
})

interface DynamicFileContentProps {
  fileName: string | null
  content: string | null
}

const DynamicFileContent: React.FC<DynamicFileContentProps> = ({ fileName, content }) => {
  return <FileContent fileName={fileName} content={content} />
}

export default DynamicFileContent