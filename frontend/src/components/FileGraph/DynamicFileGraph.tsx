import { FileData } from '@/types/types'
import { ControlsContainer, FullScreenControl, SigmaContainer, ZoomControl } from '@react-sigma/core'
import React from 'react'
import styles from './FileGraph.module.css'
import LoadGraph from './LoadGraph'

interface DynamicFileGraphProps {
  fileData: FileData | null
}

const DynamicFileGraph: React.FC<DynamicFileGraphProps> = ({ fileData }) => {
  return (
    <div className={styles.graphContainer}>
      <SigmaContainer
        className={styles.sigmaContainer}
        settings={{
          renderLabels: true,
          labelSize: 12,
          labelWeight: 'bold',
          defaultNodeColor: '#999',
          defaultEdgeColor: '#ccc',
          nodeBorderColor: '#000',
          nodeHoverColor: '#000',
          defaultNodeBorderWidth: 2,
          labelRenderedSizeThreshold: 6,
          labelDensity: 0.07,
          labelGridCellSize: 60,
          zIndex: true
        }}
      >
        <LoadGraph fileData={fileData} />
        <ControlsContainer position={'bottom-right'}>
          <ZoomControl />
          <FullScreenControl />
        </ControlsContainer>
      </SigmaContainer>
    </div>
  )
}

export default DynamicFileGraph