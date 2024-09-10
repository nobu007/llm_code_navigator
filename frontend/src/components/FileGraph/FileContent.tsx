import React from 'react'

interface FileContentProps {
  fileName: string | null
  content: string | null
}

const FileContent: React.FC<FileContentProps> = ({ fileName, content }) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-4">
      <h2 className="text-xl font-semibold mb-2">File Content</h2>
      {fileName ? (
        <>
          <p className="text-sm text-gray-600 mb-2">{fileName}</p>
          <pre className="bg-gray-100 p-2 rounded text-sm overflow-x-auto">
            {content || 'Loading...'}
          </pre>
        </>
      ) : (
        <p className="text-gray-600">Select a file to view its content</p>
      )}
    </div>
  )
}

export default FileContent