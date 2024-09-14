import { FileNode, Relationship } from '@/types/types'
import { ControlsContainer, FullScreenControl, SigmaContainer, ZoomControl } from '@react-sigma/core'
import React from 'react'
import LoadGraph from './LoadGraph'

interface DynamicSigmaContainerProps {
  files: FileNode[] | undefined
  relationships: Relationship[] | undefined
}

const DynamicSigmaContainer: React.FC<DynamicSigmaContainerProps> = ({ files, relationships }) => {
  return (
    <SigmaContainer
      style={{ height: '100%', width: '100%' }}
      settings={{
        allowInvalidContainer: true,
        renderLabels: true,
        labelSize: 12,
        labelWeight: 'bold',
        defaultNodeColor: '#999',
        defaultEdgeColor: '#ccc',
        defaultNodeBorderWidth: 2,
        defaultNodeBorderColor: '#000',
      }}
    >
      <LoadGraph files={files} relationships={relationships} />
      <ControlsContainer position={'bottom-right'}>
        <ZoomControl />
        <FullScreenControl />
      </ControlsContainer>
    </SigmaContainer>
  )
}

export default DynamicSigmaContainer