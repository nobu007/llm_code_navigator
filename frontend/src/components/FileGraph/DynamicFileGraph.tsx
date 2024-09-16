import { FileData, FileNode } from '@/types/types';
import { Box, Portal, useColorModeValue } from '@chakra-ui/react';
import { ControlsContainer, FullScreenControl, SigmaContainer, ZoomControl } from "@react-sigma/core";
import "@react-sigma/core/lib/react-sigma.min.css";
import React, { useEffect, useRef, useState } from 'react';
import LoadGraph from './LoadGraph';
import NodeMenu from './NodeMenu';

interface FileGraphProps {
  fileData: FileData
  onNodeSelect: (file: FileNode) => void
}

const DynamicFileGraph: React.FC<FileGraphProps> = ({ fileData, onNodeSelect }) => {
  const bgColor = useColorModeValue('white', 'gray.800')
  const [containerReady, setContainerReady] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)
  const [selectedNode, setSelectedNode] = useState<FileNode | null>(null)
  const [menuPosition, setMenuPosition] = useState({ x: 0, y: 0 })

  useEffect(() => {
    setContainerReady(true)
    if (containerRef.current) {
      containerRef.current.getBoundingClientRect()
    }
  }, [])

  const handleNodeClick = (file: FileNode, event: MouseEvent) => {
    setSelectedNode(file)
    setMenuPosition({ x: event.clientX, y: event.clientY })
  }

  const handleViewContent = () => {
    if (selectedNode) {
      onNodeSelect(selectedNode)
    }
    setSelectedNode(null)
  }

  if (fileData.files.length === 0) {
    return (
      <Box width="100%" height="500px" bg={bgColor} borderRadius="md" display="flex" alignItems="center" justifyContent="center">
        <Text>No files to display</Text>
      </Box>
    )
  }

  return (
    <Box ref={containerRef} width="100%" height="500px" bg={bgColor} borderRadius="md" overflow="hidden" position="relative">
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
          <LoadGraph files={fileData.files} relationships={fileData.relationships} onNodeClick={handleNodeClick} />
          <ControlsContainer position={"bottom-right"}>
            <ZoomControl />
            <FullScreenControl />
          </ControlsContainer>
        </SigmaContainer>
      )}
      <Portal>
        <Box position="absolute" left={menuPosition.x} top={menuPosition.y}>
          <NodeMenu
            selectedNode={selectedNode}
            onViewContent={handleViewContent}
            onClose={() => setSelectedNode(null)}
          />
        </Box>
      </Portal>
    </Box>
  )
}

export default DynamicFileGraph