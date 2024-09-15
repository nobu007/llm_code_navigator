import { FileData } from '@/types/types'
import dynamic from 'next/dynamic'
import React from 'react'

const FileGraph = dynamic(() => import('./FileGraph'), {
  ssr: false,
  loading: () => <p>Loading file graph...</p>
})

interface DynamicFileGraphProps {
  fileData: FileData
}

const DynamicFileGraph: React.FC<DynamicFileGraphProps> = ({ fileData }) => {
  return <FileGraph files={fileData.files} relationships={fileData.relationships} />
}

export default DynamicFileGraph