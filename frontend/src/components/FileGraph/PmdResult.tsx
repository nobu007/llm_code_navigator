import React from 'react'

interface PmdResultProps {
  result: string | null
}

const PmdResult: React.FC<PmdResultProps> = ({ result }) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-4">
      <h2 className="text-2xl font-semibold mb-4">PMD Analysis</h2>
      {result ? (
        <pre className="bg-muted p-4 rounded-md text-sm overflow-x-auto whitespace-pre-wrap">
          <code>{result}</code>
        </pre>
      ) : (
        <p className="text-muted-foreground">No analysis available</p>
      )}
    </div>
  )
}

export default PmdResult
