import { FileData, FileNode } from '@/types/types';
import { Box, useColorModeValue } from '@chakra-ui/react';
import { ControlsContainer, FullScreenControl, SigmaContainer, ZoomControl } from "@react-sigma/core";
import "@react-sigma/core/lib/react-sigma.min.css";
import React, { useEffect, useRef, useState } from 'react';
import LoadGraph from './LoadGraph';

interface FileGraphProps {
  fileData: FileData
  onNodeClick: (file: FileNode) => void
}

const DynamicFileGraph: React.FC<FileGraphProps> = ({ fileData, onNodeClick }) => {
  const bgColor = useColorModeValue('white', 'gray.800')
  const [containerReady, setContainerReady] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    setContainerReady(true)
    if (containerRef.current) {
      containerRef.current.getBoundingClientRect()
    }
  }, [])

  if (fileData.files.length === 0) {
    return (
      <Box width="100%" height="500px" bg={bgColor} borderRadius="md" display="flex" alignItems="center" justifyContent="center">
        <Text>No files to display</Text>
      </Box>
    )
  }

  return (
    <Box ref={containerRef} width="100%" height="500px" bg={bgColor} borderRadius="md" overflow="hidden">
      {containerReady && (
        <SigmaContainer
          style={{ width: '100%', height: '100%' }}
          settings={{
            allowInvalidContainer: true,
            renderEdgeLabels: true,
            labelSize: 12,
            labelWeight: 'bold',
            defaultEdgeType: 'arrow',
          }}
        >
          <LoadGraph files={fileData.files} relationships={fileData.relationships} onNodeClick={onNodeClick} />
          <ControlsContainer position={"bottom-right"}>
            <ZoomControl />
            <FullScreenControl />
          </ControlsContainer>
        </SigmaContainer>
      )}
    </Box>
  )
}

export default DynamicFileGraph