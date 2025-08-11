import dynamic from 'next/dynamic'
import React from 'react'

const PmdResult = dynamic(() => import('./PmdResult'), {
  ssr: false,
  loading: () => <p>Loading PMD result...</p>
})

interface DynamicPmdResultProps {
  result: string | null
}

const DynamicPmdResult: React.FC<DynamicPmdResultProps> = ({ result }) => {
  return <PmdResult result={result} />
}

export default DynamicPmdResult
