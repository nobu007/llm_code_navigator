import React from 'react'
import { PmdResult as PmdResultType } from '@/types/types'

interface PmdResultProps {
  result: PmdResultType | null
}

const PmdResult: React.FC<PmdResultProps> = ({ result }) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-4">
      <h2 className="text-2xl font-semibold mb-4">PMD Analysis</h2>
      {result ? (
        <div>
          <div className="mb-4 p-3 bg-gray-50 rounded-md">
            <h3 className="font-semibold text-lg mb-2">Summary</h3>
            <p><strong>File:</strong> {result.summary.fileAnalyzed}</p>
            <p><strong>Total Violations:</strong> {result.summary.totalViolations}</p>
            {result.summary.pmdVersion && (
              <p><strong>PMD Version:</strong> {result.summary.pmdVersion}</p>
            )}
          </div>
          
          {result.violations.length > 0 ? (
            <div>
              <h3 className="font-semibold text-lg mb-3">Violations</h3>
              <div className="space-y-3">
                {result.violations.map((violation, index) => (
                  <div key={index} className="border-l-4 border-red-400 pl-4 py-2 bg-red-50">
                    <div className="flex justify-between items-start mb-1">
                      <span className="font-medium text-red-800">{violation.rule}</span>
                      <span className="text-sm bg-red-200 text-red-800 px-2 py-1 rounded">
                        Priority {violation.priority}
                      </span>
                    </div>
                    <p className="text-gray-700 mb-1">{violation.message}</p>
                    <p className="text-sm text-gray-500">
                      Line {violation.line}, Column {violation.column}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="p-3 bg-green-50 border-l-4 border-green-400">
              <p className="text-green-800">No violations found! 🎉</p>
            </div>
          )}
        </div>
      ) : (
        <p className="text-muted-foreground">No analysis available</p>
      )}
    </div>
  )
}

export default PmdResult
