import { FileNode } from '@/types/types'
import { ChevronDownIcon } from "@chakra-ui/icons"
import { Button, Menu, MenuButton, MenuItem, MenuList } from "@chakra-ui/react"
import React from 'react'

interface NodeMenuProps {
  selectedNode: FileNode | null
  onViewContent: () => void
  onClose: () => void
}

const NodeMenu: React.FC<NodeMenuProps> = ({ selectedNode, onViewContent, onClose }) => {
  if (!selectedNode) return null

  return (
    <Menu isOpen={true} onClose={onClose}>
      <MenuButton as={Button} rightIcon={<ChevronDownIcon />}>
        {selectedNode.name}
      </MenuButton>
      <MenuList>
        <MenuItem onClick={onViewContent}>View Content</MenuItem>
        {/* Add more menu items here as needed */}
      </MenuList>
    </Menu>
  )
}

export default NodeMenu