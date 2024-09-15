import { FileEdge, FileNode } from '@/types/types'
import dynamic from 'next/dynamic'
import React from 'react'

const SigmaContainer = dynamic(() => import('@react-sigma/core').then(mod => mod.SigmaContainer), { ssr: false })
const ControlsContainer = dynamic(() => import('@react-sigma/core').then(mod => mod.ControlsContainer), { ssr: false })
const ZoomControl = dynamic(() => import('@react-sigma/core').then(mod => mod.ZoomControl), { ssr: false })
const FullScreenControl = dynamic(() => import('@react-sigma/core').then(mod => mod.FullScreenControl), { ssr: false })

interface DynamicSigmaContainerProps {
  files: FileNode[]
  relationships: FileEdge[]
  children: React.ReactNode
}

const DynamicSigmaContainer: React.FC<DynamicSigmaContainerProps> = ({ files, relationships, children }) => {
  return (
    <div style={{ height: "500px", width: "100%" }}>
      <SigmaContainer
        style={{ height: "100%", width: "100%" }}
        settings={{
          renderLabels: true,
          labelSize: 12,
          labelWeight: 'bold',
          defaultNodeColor: '#999',
          defaultEdgeColor: '#ccc',
          labelRenderedSizeThreshold: 6,
          labelDensity: 0.07,
          labelGridCellSize: 60,
          zIndex: true,
          allowInvalidContainer: true,
        }}
      >
        {children}
        <ControlsContainer position={'bottom-right'}>
          <ZoomControl />
          <FullScreenControl />
        </ControlsContainer>
      </SigmaContainer>
    </div>
  )
}

export default DynamicSigmaContainer