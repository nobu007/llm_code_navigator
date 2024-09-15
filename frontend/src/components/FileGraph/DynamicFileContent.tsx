import dynamic from 'next/dynamic'
import React from 'react'

const DynamicFileContent = dynamic(() => import('./FileContent'), {
  ssr: false,
  loading: () => <p>Loading file content...</p>
})

interface FileContentProps {
  fileName: string | null
  content: string | null
}

const FileContentWrapper: React.FC<FileContentProps> = ({ fileName, content }) => {
  return <DynamicFileContent fileName={fileName} content={content} />
}

export default FileContentWrapper