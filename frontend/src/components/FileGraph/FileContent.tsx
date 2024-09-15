import React from 'react'

interface FileContentProps {
  fileName: string | null
  content: string | null
}

const FileContent: React.FC<FileContentProps> = ({ fileName, content }) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-4">
      <h2 className="text-2xl font-semibold mb-4">File Content</h2>
      {fileName ? (
        <>
          <p className="text-sm text-muted-foreground mb-2" aria-label="File name">{fileName}</p>
          <pre className="bg-muted p-4 rounded-md text-sm overflow-x-auto whitespace-pre-wrap" aria-label="File content">
            <code>{content || 'Loading...'}</code>
          </pre>
        </>
      ) : (
        <p className="text-muted-foreground">Select a file to view its content</p>
      )}
    </div>
  )
}

export default FileContent