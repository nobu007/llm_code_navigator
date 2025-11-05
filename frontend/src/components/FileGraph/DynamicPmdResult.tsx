import dynamic from 'next/dynamic'
import React from 'react'
import { PmdResult as PmdResultType } from '@/types/types'

const PmdResult = dynamic(() => import('./PmdResult'), {
  ssr: false,
  loading: () => <p>Loading PMD result...</p>
})

interface DynamicPmdResultProps {
  result: string | null
}

const DynamicPmdResult: React.FC<DynamicPmdResultProps> = ({ result }) => {
  let parsedResult: PmdResultType | null = null
  
  if (result) {
    try {
      parsedResult = JSON.parse(result) as PmdResultType
    } catch (error) {
      console.error('Failed to parse PMD result:', error)
    }
  }
  
  return <PmdResult result={parsedResult} />
}

export default DynamicPmdResult
